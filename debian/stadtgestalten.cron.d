# optional:
#    MAILTO=admin@example.org

# process incoming mails
*/3 * * * * stadtctl getmail | grep -v ^INFO:

# calculate scores for groups and users
23  * * * * stadtctl update_scores
