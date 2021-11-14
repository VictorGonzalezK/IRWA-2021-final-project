# IRWA-2021-final-project-part-1
The code is created to run in as a python notebook. 
Created in a jupyter notebook enviroment with the following python and libraries versions:
	- Python version 3.7.4
	- nltk version 3.4.5
	- json version 2.0.9
	- pycountry version 20.7.3
	- re version 2.2.1
	- numpy version 1.17.2
	- pandas version 1.0.1
	- gensim version 4.1.2
	- matplotlib version 2.2.3
 	- sklearn version 0.19.2

The code should be run in the established order of cells.
This is because some functions may depend on others to run correctly and they are already seated in the correct order.
Howevwer the correct order is the following:
	1. Deploy load_data function
	2. Run load_data function with the desired file load (should be in the same directory)
	3. Deploy iso_leng_translate function
	4. Deploy create_stopword_dict function 
	5. Run create_stopword_dict with the dataset of tweets loaded before and save the output in a variable
	6. Deploy clean_data function
	7. Deploy create_index
	8. Run create_index and save the output in a variables called inverted_index, tf, idf for later usage
	9. Deploy rankTweets
	10. Deploy get_hashtags
	11. Deploy tweet_Searcher
	12. Deploy query_search
	13. Run query_search with a desired query in the format ({"full_text":"query", "lang":"query lang"}) 
	    and boolean score False to print the outputs of your searcher
EVALUATION:
	Evaluation part needs first to create the pandas dataframe that will be used to evaluation
	then you just can deploy all functions in the correct order and run them to do different evaluations.
	Creation of dataframe (they use query search so the need to be done after previous deployments):
	14. Get some queries in specified format
	15. Run query_search in True mode to get scores for each query-tweet and save the results in the pandas
	16. Do the grou truth as expert and inser them on the pandas
	Correct order for evaluation functions (they need from previous dataset):
	17. Deploy precision_at_k
	18. Deploy avg_precision_at_k
	19. Deploy map_at_k
	20. Deploy mrr_at_k (but it is independndet from other evaluations could be run in step 17)
	21. Deploy dcg_at_k (can be also run in step 17)
	22. Deploy ndcg_at_k (always after deploy dcg_at_k)
	23. Run any of the evaluation functions (each function can be run inmediatly after its deployment)

T-SNE:
	24. Run the complete cell to make the plot
Extra functions (this functions should be run after the load of the data whenever you want):
	1. tweet_lenguageSearcher (to search for an id of a concrete language)
	2. tweet_Printer (to search with an id the original tweet and print it)

(both should be first deployed and then run)
