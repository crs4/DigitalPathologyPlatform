---
layout: default
title: Annotation Manager Configuration
parent: Installation & Usage
nav_order: 4 
---

## Annotation Manager Configuration

After deploying the platform, configure the Annotation Manager by performing the following steps:

- Create an admin user
- Create one or more reviewer accounts

### 1. Create Admin User

To create the admin (superuser) account, run the following command:

```bash
./compose.sh exec promort-web python manage.py createsuperuser
```

You will be prompted to enter:

- Username
- Email address
- Password (entered twice for confirmation)

Example output:

```bash
~/cdpp-workflows$ ./compose.sh exec promort-web python manage.py createsuperuser
WARN[0000] The "CWLDOCKER_ENV" variable is not set. Defaulting to a blank string.
WARN[0000] The "CWLDOCKER_PID" variable is not set. Defaulting to a blank string.
...
/home/lianas/cdpp-workflows/docker-compose.yaml: the attribute `version` is obsolete, it will be ignored...
Username: cdpp_admin
Email address: cdpp.admin@crs4.it
Password:
Password (again):
Superuser created successfully.
```

### 2. Create CDPP Reviewer

Once the admin user is created, log in to the Django Admin interface at:

```
http://<your_hostname>/admin/
```

Use the superuser credentials to log in. To create a reviewer account:

Click **Add user** in the Django Admin dashboard:

<a href="/assets/images/04-am_config/site_admin.png" data-lightbox="04-am_config-1">
  <img src="/assets/images/04-am_config/site_admin.png" alt="Django Admin - Add user" width="100%" />
</a>

Enter the desired username and password, then click **Save and continue editing**:

<a href="/assets/images/04-am_config/new_user-1.png" data-lightbox="04-am_config-2">
  <img src="/assets/images/04-am_config/new_user-1.png" alt="Create new user form" width="100%" />
</a>

Fill in the user's personal information and assign the user to the following groups:

- `ROIS_MANAGERS`
- `CLINICAL_MANAGERS`

<a href="/assets/images/04-am_config/new_user-2.png" data-lightbox="04-am_config-3">
  <img src="/assets/images/04-am_config/new_user-2.png" alt="Assign groups to user" width="100%" />
</a>

When finished, click **Save**.

You should now see the new user in the list:

<a href="/assets/images/04-am_config/users_recap.png" data-lightbox="04-am_config-4">
  <img src="/assets/images/04-am_config/users_recap.png" alt="Users overview list" width="100%" />
</a>

Repeat this process to create additional reviewer accounts.
