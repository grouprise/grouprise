# optional:
#    MAILTO=admin@example.org

# process incoming mails
*/3 * * * * root        chronic stadtctl getmail

# calculate scores for groups and users
23  * * * * root        chronic stadtctl update_scores

# import content from external websites
46  * * * * root        chronic stadtctl import_feeds

# send mails with django-mailer
*   * * * * root        cd /tmp && chronic sh -c "stadtctl send_mail 2>&1 | tee -a /var/log/stadtgestalten/mailer-stadtgestalten.log"
9,29,49 * * * * root    cd /tmp && chronic sh -c "stadtctl retry_deferred 2>&1 | tee -a /var/log/stadtgestalten/mailer-stadtgestalten.log"
