# IRWA-2021-final-project-part-1
The code is created to run in as a python notebook. 
Created in a jupyter notebook enviroment with the following python and libraries versions:
	- Python version 3.7.4
	- nltk version 3.4.5
	- json version 2.0.9
	- pycountry version 20.7.3
	- re version 2.2.1

The code should be run in the established order of cells.
This is because some functions may depend on others to run correctly and they are already seated in the correct order.
Howevwer the correct order is the following:
	1. Deploy load_data function
	2. Run load_data function with the desired file load (should be un the same directory)
	3. Deploy iso_leng_translate function
	4. Deploy create_stopword_dict function
	5. Run create_stopword_dict with the dataset of tweets loaded before and save the output in a variable
	6. Deploy clean_data function (main function)
	7. Run the clean_data function as main function you get the desired output (a dictionary with the document text proceced and stored by the id of og tweet)

Extra functions (this functions should be run after the load of the data whenever you want):
	1. tweet_lenguageSearcher (to search for an id of a concrete language, serves to get some ids and use it to print an example of clean tweet processed before)
	2. tweet_Searcher (to search with an id the original tweet, can serve to compare correctness of the pre-process)

(both should be first deployed and then run)
