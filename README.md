# cilantro - This is a personal finance app using bank transactions

Here are the instructions to use this repo

Transaction file as per availability on bank website

Amex - date range
BOFA - statement month wise
Chase - year to date
Citi - year to date or statement month-wise
USB - date range
WF - date range

So download all the transactions and name them as "Transactions_<Bank>xxx.csv"
    
The code uses labeledTransactions.csv file for training a simple Bayesian model to recognize the nature of transactions.
   
It aggregates all the transactions found in the transaction folder and then attempts to label them based on labeled transactions
    
If there are new unlabeled transactions present, follow these steps
    
1. Create some labeled transactions and store them as "labeledTransactions.csv"
2. Download all the unlabeled statements from your bank and put them in the transactions folder
3. Uncomment the line "helper.labelTransactions(folder)" (this labels the unlabled transactions)
4. Comment the line "aggregateDf.to_csv(folder+'labeledTransactions.csv', index=False)" inside helper.py inside function "helper.labelTransactions(folder)"
5. Run the code. The code will display all the labeled transactions and some transactions that are unlabeled.
6. If everthing is labeled correctly, uncomment the line "aggregateDf.to_csv(folder+'labeledTransactions.csv', index=False)" so it writes everything to the file
7. If there are some transactions that are not labeled correctly or not labeled, uncomment the line "aggregateDf.to_csv(folder+'labeledTransactions.csv', index=False)" so it can still write the file and you can manually add the correct label (just one transaction should be good for an unseen label)
    
If all transactions present are labeled, simply run the script.
    
