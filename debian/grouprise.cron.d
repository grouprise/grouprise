# calculate scores for groups and users
23  * * * * _grouprise        chronic grouprisectl update_scores

# import content from external websites
46  * * * * _grouprise        chronic grouprisectl import_feeds

# update search index
*/5 * * * * _grouprise        chronic grouprisectl update_index --remove
