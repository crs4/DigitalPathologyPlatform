import requests
import logging
import sys
import re
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
            self.session_id = self.promort_client.cookies.get('sessionid')
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
            'sessionid': self.session_id
        }
        payload.update(auth_payload)

    def _get_request_headers(self):
        return {
            'Set-Cookie': 'csrftoken=%s, sessionid=%s' % (self.csrf_token, self.session_id)
        }

    def _split_slide_name(self, slide_name):
        regex = re.compile(r'[0-9]+-[0-9]+')
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
        elif response.status_code == requests.codes.BAD:
            self.logger.warn('Unable to create case with ID %r', case_id)

    def _save_slide(self, slide_id, case, omero_id, image_type):
        payload = {
            'id': slide_id,
            'case': case,
            'omero_id': omero_id,
            'image_type': image_type
        }
        self._update_payload(payload)
        url = urljoin(self.promort_host, 'api/slides/')
        response = self.promort_client.post(url, payload)
        if response.status_code == requests.codes.CREATED:
            self.logger.info('Slide with ID %r created', slide_id)
        elif response.status_code == requests.codes.BAD:
            self.logger.warn('Unable to create slide with ID %r' , slide_id)

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

    def _serialize_slide_map(self, slides_map):
        for case, slides in slides_map.iteritems():
            self._save_case(case)
            for slide in slides:
                self._save_slide(slide['name'], case,
                                 slide['omero_id'], slide['img_type'])

    def run(self):
        self._promort_login()
        slides_map = self._get_ome_images()
        self._serialize_slide_map(slides_map)
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
    importer.run()


if __name__ == '__main__':
    main(sys.argv[1:])