# optional:
#    MAILTO=admin@example.org

# process incoming mails
*/3 * * * * root    stadtctl getmail | grep -v ^INFO:

# calculate scores for groups and users
23  * * * * root    stadtctl update_scores

# import content from external websites
46  * * * * root    stadtctl import_feeds
