import requests
import logging
import sys
import re
import random
from argparse import ArgumentParser
from urlparse import urljoin


class SlidesImporter(object):
    def __init__(self, ome_host, promort_host, promort_user, promort_passwd,
                 log_level='INFO', log_file=None):
        self.ome_host = ome_host
        self.promort_host = promort_host
        self.promort_user = promort_user
        self.promort_passwd = promort_passwd
        self.logger = self.get_logger(log_level, log_file)
        self.csrf_token = None
        self.session_id = None
        self.promort_client = requests.Session()

    def get_logger(self, log_level='INFO', log_file=None, mode='a'):
        LOG_FORMAT = '%(asctime)s|%(levelname)-8s|%(message)s'
        LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'

        logger = logging.getLogger('mirax_importer')
        if not isinstance(log_level, int):
            try:
                log_level = getattr(logging, log_level)
            except AttributeError:
                raise ValueError('Unsupported literal log level: %s' % log_level)
        logger.setLevel(log_level)
        logger.handlers = []
        if log_file:
            handler = logging.FileHandler(log_file, mode=mode)
        else:
            handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _promort_login(self):
        url = urljoin(self.promort_host, 'api/auth/login/')
        payload = {'username': self.promort_user, 'password': self.promort_passwd}
        response = self.promort_client.post(url, json=payload)
        if response.status_code == requests.codes.OK:
            self.csrf_token = self.promort_client.cookies.get('csrftoken')
            self.session_id = self.promort_client.cookies.get('promort_sessionid')
        else:
            self.logger.error('Unable to perform login')
            sys.exit('Unable to perform login')

    def _promort_logout(self):
        payload = {}
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/auth/logout/')
        response = self.promort_client.post(url, payload)
        self.logger.info('Logout response code %r', response.status_code)

    def _update_payload(self, payload):
        auth_payload = {
            'csrfmiddlewaretoken': self.csrf_token,
            'promort_sessionid': self.session_id
        }
        payload.update(auth_payload)

    def _get_request_headers(self):
        return {
            'Set-Cookie': 'csrftoken=%s, sessionid=%s' % (self.csrf_token, self.session_id)
        }

    def _split_slide_name(self, slide_name):
        regex = re.compile(r'[a-zA-Z0-9]+-[0-9]+')
        if regex.match(slide_name):
            return slide_name.split('-')
        else:
            return None, None

    def _save_case(self, case_id):
        payload = {
            'id': case_id
        }
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/cases/')
        response = self.promort_client.post(url, payload)
        if response.status_code == requests.codes.CREATED:
            self.logger.info('Case with ID %r created', case_id)
            return True
        elif response.status_code in (requests.codes.BAD, requests.codes.FORBIDDEN):
            self.logger.warn('Unable to create case with ID %r', case_id)
            return False

    def _check_case_existence(self, case_id):
        url = urljoin(self.promort_host, 'api/cases/%s/' % case_id)
        response = self.promort_client.get(url)
        try:
            response.json()
            self.logger.info('Case with ID %s exists', case_id)
            return True
        except ValueError:
            # default landing page
            self.logger.info('There is no case with ID %s', case_id)
            return False

    def _check_slide_existence(self, slide_id):
        url = urljoin(self.promort_host, 'api/slides/%s/' % slide_id)
        response = self.promort_client.get(url)
        try:
            response.json()
            self.logger.info('Slide with ID %s exists', slide_id)
            return True
        except ValueError:
            # default landing page
            self.logger.info('There is no slide with ID %s', slide_id)
            return False

    def _save_slide(self, slide_id, case, omero_id, image_type, image_mpp):
        payload = {
            'id': slide_id,
            'case': case,
            'omero_id': omero_id,
            'image_type': image_type,
            'image_microns_per_pixel': image_mpp
        }
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/slides/')
        response = self.promort_client.post(url, payload)
        if response.status_code == requests.codes.CREATED:
            self.logger.info('Slide with ID %r created', slide_id)
            return True
        elif response.status_code == requests.codes.BAD:
            self.logger.warn('Unable to create slide with ID %r', slide_id)
            return False

    def _relink_slide(self, slide_id, omero_id, image_type):
        payload = {
            'omero_id': omero_id,
            'image_type': image_type
        }
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/slides/%s/' % slide_id)
        response = self.promort_client.put(url, payload, headers={'X-csrftoken': self.csrf_token})
        if response.status_code == requests.codes.OK:
            self.logger.info('Slide with ID %s updated', slide_id)
            return True
        else:
            self.logger.warn('Unable to update slide with ID %s', slide_id)
            return False

    def _get_ome_images(self):
        url = urljoin(self.ome_host, 'ome_seadragon/get/images/index/')
        response = requests.get(url)
        if response.status_code == requests.codes.OK:
            self.logger.info('Slides loaded from OMERO')
            slides = response.json()
            self.logger.debug(slides)
            slides_map = dict()
            for s in slides:
                case_id, _ = self._split_slide_name(s['name'])
                if case_id:
                    slides_map.setdefault(case_id, []).append(s)
                else:
                    self.logger.warn('%s is not a valid slide name', s['name'])
            self.logger.debug(slides_map)
            return slides_map
        else:
            self.logger.error('Unable to load slides from OMERO')
            sys.exit('Unable to load slides from OMERO')

    def _get_slide_mpp(self, slide):
        if slide['img_type'] == 'OMERO_IMG':
            url = urljoin(self.ome_host, 'ome_seadragon/deepzoom/image_mpp/' +
                          slide['omero_id'] + '.dzi')
        else:
            url = urljoin(self.ome_host, 'ome_seadragon/mirax/deepzoom/image_mpp/' +
                          slide['name'] + '.dzi')
        self.logger.info(url)
        response = requests.get(url)
        if response.status_code == requests.codes.OK:
            return response.json()['image_mpp']
        else:
            return 0

    def _serialize_slides(self, relink_slides):
        slides_map = self._get_ome_images()
        for case, slides in slides_map.iteritems():
            self._save_case(case)
            case_exists = self._check_case_existence(case)
            if case_exists:
                for slide in slides:
                    slide_saved = self._save_slide(slide['name'], case, slide['omero_id'],
                                                   slide['img_type'], self._get_slide_mpp(slide))
                    if not slide_saved and relink_slides:
                        slide_exists = self._check_slide_existence(slide['name'])
                        if slide_exists:
                            self._relink_slide(slide['name'], slide['omero_id'], slide['img_type'])

    def _get_slides_map(self):
        slides_map = {}
        cases_response = self.promort_client.get(urljoin(self.promort_host, 'api/cases/'))
        if cases_response.status_code == requests.codes.OK:
            cases = cases_response.json()
            for case in cases:
                case_id = case['id']
                slides_response = self.promort_client.get(urljoin(self.promort_host, 'api/cases/%s/' % case_id))
                if slides_response.status_code == requests.codes.OK:
                    slides = slides_response.json()['slides']
                    for slide in slides:
                        slides_map.setdefault(case_id, []).append(slide['id'])
        return slides_map

    def _get_users_list(self, group):
        url = urljoin(self.promort_host, 'api/groups/%s/' % group)
        return self.promort_client.get(url)

    def _get_rois_reviewers_list(self):
        response = self._get_users_list('rois_manager')
        if response.status_code == requests.codes.OK:
            users = response.json()['users']
            self.logger.info('Loaded %d users' % len(users))
            return [u['username'] for u in users]
        else:
            self.logger.error('Unable to load users list for "rois_manager" group')
            self._promort_logout()
            sys.exit('Unable to load users list for "rois_manager" group')

    def _create_rois_annotation(self, case_id, reviewer):
        payload = dict()
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/rois_annotations/%s/%s/' % (case_id, reviewer))
        response = self.promort_client.post(url, payload)
        self.logger.info('STATUS CODE: %s', response.status_code)
        if response.status_code == requests.codes.CREATED:
            self.logger.info('Created a ROIs annotation for case %s', case_id)
            return True
        elif response.status_code in (requests.codes.BAD, requests.codes.FORBIDDEN):
            self.logger.warn('Unable to create ROIs annotation for case %s [status code %s]',
                             case_id, response.status_code)
            return False

    def _create_rois_annotation_step(self, case_id, reviewer, slide_id):
        payload = dict()
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/rois_annotations/%s/%s/%s/' % (case_id, reviewer, slide_id))
        response = self.promort_client.post(url, payload)
        if response.status_code == requests.codes.CREATED:
            self.logger.info('Create a ROIs annotation step for slide %s', slide_id)
        elif response.status_code in (requests.codes.BAD, requests.codes.FORBIDDEN):
            self.logger.warn('Unable to create ROIs annotation step for slide %s [status code %s]',
                             slide_id, response.status_code)
        elif response.status_code == requests.codes.CONFLICT:
            self.logger.error(response.json()['message'])

    def _create_rois_worklist(self):
        objs_map = self._get_slides_map()
        rois_users = self._get_rois_reviewers_list()
        for i, (case, slides) in enumerate(objs_map.iteritems()):
            reviewer = rois_users[i % len(rois_users)]
            self.logger.info('Creating ROIs annotation for case %s to user %s', case, reviewer)
            rev_created = self._create_rois_annotation(case, reviewer)
            if rev_created:
                for slide in slides:
                    self.logger.info('Creating annotation step for slide %s of case %s', slide, case)
                    self._create_rois_annotation_step(case, reviewer, slide)

    def _get_clinical_annotations_reviewers_list(self):
        response = self._get_users_list('clinical_manager')
        if response.status_code == requests.codes.OK:
            users = response.json()['users']
            self.logger.info('Loaded %d users' % len(users))
            return [u['username'] for u in users]
        else:
            self.logger.error('Unable to load users list for "clinical_manager" group')
            self._promort_logout()
            sys.exit('Unable to load users list for "clinical_manager" group')

    def _select_clinical_reviewers(self, users_list, rois_reviewer, reviewers_count):
        reviewers = []
        rct = reviewers_count
        if rois_reviewer in users_list:
            reviewers.append(rois_reviewer)
            rct -= 1
        while rct > 0:
            # TODO: optimize this....
            r = random.choice(users_list)
            if r not in reviewers:
                reviewers.append(r)
                rct -= 1
        return reviewers


    def _get_rois_annotations_list(self):
        annotations_list = []
        url = urljoin(self.promort_host, 'api/rois_annotations/')
        response = self.promort_client.get(url)
        if response.status_code == requests.codes.OK:
            for annotation in response.json():
                annotations_list.append({
                    'id': annotation['id'],
                    'reviewer': annotation['reviewer'],
                    'case': annotation['case']
                })
        return annotations_list

    def _get_rois_annotation_steps_list(self, case_id):
        steps_list = []
        url = urljoin(self.promort_host, 'api/rois_annotations/%s/' % case_id)
        response = self.promort_client.get(url)
        if response.status_code == requests.codes.OK:
            for annotation in response.json():
                reviewer = annotation['reviewer']
                url = urljoin(self.promort_host, 'api/rois_annotations/%s/%s/' % (case_id, reviewer))
                ann_response = self.promort_client.get(url)
                if ann_response.status_code == requests.codes.OK:
                    for step in ann_response.json()['steps']:
                        steps_list.append({
                            'id': step['id'],
                            'slide': step['slide'],
                            'quality_control': step['slide_quality_control']
                        })
        return steps_list

    def _create_clinical_annotation(self, case_id, reviewer, rois_annotation_id):
        payload = dict()
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/clinical_annotations/%s/%s/%s/' % (case_id, reviewer,
                                                                                 rois_annotation_id))
        response = self.promort_client.post(url, payload)
        if response.status_code == requests.codes.CREATED:
            self.logger.info(
                'Created a clinical annotation for case %s assigned to reviewer %s linked to ROIs annotation %s' %
                (case_id, reviewer, rois_annotation_id))
        elif response.status_code in (requests.codes.BAD, requests.codes.FORBIDDEN):
            self.logger.warn('Unable to create clinical annotation [status code %s]' % response.status_code)
        elif response.status_code == requests.codes.CONFLICT:
            self.logger.error(response.json()['message'])

    def _start_clinical_annotation(self, case_id, reviewer, rois_annotation_id):
        payload = {'action': 'START'}
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/clinical_annotations/%s/%s/%s/' % (case_id, reviewer,
                                                                                 rois_annotation_id))
        response = self.promort_client.put(url, payload, headers={'X-csrftoken': self.csrf_token})
        if response.status_code == requests.codes.OK:
            self.logger.info('Started clinical annotation')
        elif response.status_code == requests.codes.CONFLICT:
            self.logger.warn('Unable to start clinical annotation')

    def _start_and_close_clinical_annotation_step(self, case_id, reviewer, rois_annotation_id, slide_id):
        self._start_clinical_annotation(case_id, reviewer, rois_annotation_id)
        # start clinical annotation step
        payload = {'action': 'START'}
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/clinical_annotations/%s/%s/%s/%s/' % (case_id, reviewer,
                                                                                    rois_annotation_id, slide_id))
        response = self.promort_client.put(url, payload, headers={'X-csrftoken': self.csrf_token})
        if response.status_code == requests.codes.OK:
            self.logger.info('Started clinical annotation step')
            payload['action'] = 'FINISH'
            response = self.promort_client.put(url, payload, headers={'X-csrftoken': self.csrf_token})
            if response.status_code == requests.codes.OK:
                self.logger.info('Closed clinical_annotation_step')
            elif response.status_code == requests.codes.CONFLICT:
                self.logger.warn('Unable to close clinical annotation step')
        elif response.status_code == requests.codes.CONFLICT:
            self.logger.warn('Unable to start clinical annotation step')

    def _create_clinical_annotation_step(self, case_id, reviewer, rois_annotation_id, slide_id, immediate_close):
        payload = dict()
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/clinical_annotations/%s/%s/%s/%s/' % (case_id, reviewer,
                                                                                    rois_annotation_id, slide_id))
        response = self.promort_client.post(url, payload)
        if response.status_code == requests.codes.CREATED:
            self.logger.info('Created a clinical annotation step for slide %s' % slide_id)
            if immediate_close:
                self.logger.info('START and CLOSE this clinical annotation step')
                self._start_and_close_clinical_annotation_step(case_id, reviewer, rois_annotation_id, slide_id)
        elif response.status_code in (requests.codes.BAD, requests.codes.FORBIDDEN):
            self.logger.warn('Unable to create clinical annotation step [status code %s]' % response.status_code)
        elif response.status_code == requests.codes.CONFLICT:
            self.logger.error(response.json()['message'])

    def _create_clinical_annotations_worklist(self, reviewers_count):
        clinical_users = self._get_clinical_annotations_reviewers_list()
        annotations_list = self._get_rois_annotations_list()
        for annotation in annotations_list:
            steps_list = self._get_rois_annotation_steps_list(annotation['case'])
            reviewers = self._select_clinical_reviewers(clinical_users, annotation['reviewer'],
                                                        reviewers_count)
            for r in reviewers:
                self._create_clinical_annotation(annotation['case'], r, annotation['id'])
                for step in steps_list:
                    close_clinical_annotation = not step['quality_control'] is None and \
                                                not step['quality_control']['adequate_slide']
                    self._create_clinical_annotation_step(annotation['case'], r, annotation['id'], step['slide'],
                                                          close_clinical_annotation)

    def run(self, create_rois_worklist, create_clinical_worklist, reviewers_count, relink_slides):
        self._promort_login()
        self._serialize_slides(relink_slides)
        if create_rois_worklist:
            self._create_rois_worklist()
        if create_clinical_worklist:
            self._create_clinical_annotations_worklist(reviewers_count)
        self._promort_logout()


def get_parser():
    parser = ArgumentParser('Import slides from OMERO into ProMort')
    parser.add_argument('--omero-host', type=str, required=True,
                        help='OMERO.web host HTTP address')
    parser.add_argument('--promort-host', type=str, required=True,
                        help='ProMort host HTTP address')
    parser.add_argument('--promort-user', type=str, required=True,
                        help='ProMort user')
    parser.add_argument('--promort-password', type=str, required=True,
                        help='ProMort password')
    parser.add_argument('--rois-worklist', action='store_true',
                        help='create ROIs annotations worklist')
    parser.add_argument('--clinical-worklist', action='store_true',
                        help='create clinical annotations worklist')
    parser.add_argument('--reviewers', type=int, default=2,
                        help='number of clinical reviewers')
    parser.add_argument('--relink-slides', action='store_true',
                        help='Relink slides to their OMERO images')
    parser.add_argument('--log-level', type=str, default='INFO',
                        help='log level (default=INFO)')
    parser.add_argument('--log-file', type=str, default=None,
                        help='log file (default=stderr)')
    return parser


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)
    importer = SlidesImporter(args.omero_host, args.promort_host,
                              args.promort_user, args.promort_password,
                              args.log_level, args.log_file)
    importer.run(args.rois_worklist, args.clinical_worklist, args.reviewers,
                 args.relink_slides)


if __name__ == '__main__':
    main(sys.argv[1:])
