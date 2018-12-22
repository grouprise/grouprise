# process incoming mails
# The LMTP daemon (since grouprise 2.3) is supposed to handle incoming mail in the future.
# This requires changes of the SMTP server setup. We will start with single recipient groups, until
# all traffic is handled by LMTP.
*/3 * * * * root        chronic sh -c 'stadtctl getmail 2>&1 | grep -vE "^(INFO:|WARNING:django_mailbox.models:.*content-transfer-encoding)"'

# calculate scores for groups and users
23  * * * * root        chronic stadtctl update_scores

# import content from external websites
46  * * * * root        chronic stadtctl import_feeds

# send mails with django-mailer
*   * * * * root        cd /tmp && chronic sh -c "stadtctl send_mail 2>&1 | tee -a /var/log/stadtgestalten/mailer-stadtgestalten.log"
9,29,49 * * * * root    cd /tmp && chronic sh -c "stadtctl retry_deferred 2>&1 | tee -a /var/log/stadtgestalten/mailer-stadtgestalten.log"

# update search index
*/5 * * * * root        chronic stadtctl update_index --remove
