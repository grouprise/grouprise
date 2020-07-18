# process incoming mails
# The LMTP daemon (since grouprise 2.3) is supposed to handle incoming mail in the future.
# This requires changes of the SMTP server setup. We will start with single recipient groups, until
# all traffic is handled by LMTP.
*/3 * * * * _grouprise        chronic sh -c 'grouprisectl getmail 2>&1 | grep -vE "^(INFO:|WARNING:django_mailbox.models:.*content-transfer-encoding)"'

# calculate scores for groups and users
23  * * * * _grouprise        chronic grouprisectl update_scores

# import content from external websites
46  * * * * _grouprise        chronic grouprisectl import_feeds

# send mails with django-mailer
*   * * * * _grouprise        cd /tmp && chronic sh -c "grouprisectl send_mail 2>&1 | tee -a /var/log/grouprise/mailer-grouprise.log"
9,29,49 * * * * _grouprise    cd /tmp && chronic sh -c "grouprisectl retry_deferred 2>&1 | tee -a /var/log/grouprise/mailer-grouprise.log"

# update search index
*/5 * * * * _grouprise        chronic grouprisectl update_index --remove
