mama-survey
===========

mama-survey provides a simple multiple-choice question-only survey capability for the askMAMA
mobi site. 

Administrators can create questionnaires in the admin site, and view and export answers sheets. 

The first available questionnaire will only be showed to users on their 2nd login. A link will
also be displayed at the bottom of the home page.

Users can choose to complete the questionnaire immediately, later, or decline to participate.
Decline will apply to all future questionnaires as well.

Users can bail out of a questionnaire halfway, and resume it later.

Statistics about completed, aborted and declined questionnaires will be sent to the apporpriate holodeck metrics tracker on a regular basis.


Dependencies
------------

System libraries
****************

Python packages
***************

Usage
-----

For production, install the application in the askMAMA site with:

::
python setup.py install
::

For development, install the application in the askMAMA development site with:

::
python setup.py develop
::

Settings
********
The following settings must be added to settings.py:
::
INSTALLED_APPS {
    .....
    'survey',
    ....
}
::
