## Documentation of 1st Project Implementation for IPP 2023/2024 
### Name and surname: Iaroslav Zhdanovich
### Login: xzhdan00

## Parse.py

To accomplish the task, the script is divided into a sequence of functions:
* main() function
* lexer() function
* syntaxer() function
* valueCheck() function
* genXML() function

 Now, let's examine the functionality of each function separately
 
 ### main():
 
The main() function is the core of the program. It is launched at script startup being wrapped in a "try-except" block to be able to handle exceptions raised during program execution.
First, the main() function checks if the --help argument is present when the script starts, and if it is present, it writes a help message to the standard output and terminates the program. Then it reads the standard output and calls the lexer() function, the argument of which is the data received from the standard output. After executing the lexer() function, the syntaxer() and genXML() functions are called with arguments that are the output of the lexer() function. At the end, if the above functions are successfully executed, the program is terminated.

### lexer():

The lexer() function receives data from the standard input of the program. It splits the data first into lines and then into tokens, ignoring empty lines and comments. Using a regular expression pattern for the header, it checks if the 1st found token is a header, and if not, raises an exception (there is also a built-in check for multiple headers). Then it checks the tokens line by line using regular expressions defined inside the function for each token type as follows: 1st token must be operational code followed by n-operands. The checks are performed sequentially:

If a match with the frame pattern is found, a further check of the variable name is performed. Then the token is assigned the type "var"
If a match with a symbol pattern is found, the function, valueCheck() is called to check the value. Then the token is assigned the type specified in the token.

If a match with the type pattern is found, the operational code is checked: if the operational code we received is in the label_usage list, which contains all operational codes that work with labels, the token is assigned the type "label", otherwise it is assigned the type "type". This check is made because the IPPcode24 language is context-dependent and the same token can belong to different types depending on its position in the code

If a match with a variable name is found, the token is assigned the type "label" (label names have the same lexical rules of writing as variable names). 

If the received token fails any of the checks above, an appropriate exception is raised. 

At the end, the function returns two lists: to_syntaxer, containing only the operating codes and the types of their associated tokens (created for syntax checking since token names are not important for it), and lexer_out, containing the operating codes, tokens and their types.

### valueCheck():

The valueCheck() function takes 2 arguments: type and value. Then value is checked according to its type using regular expressions and usual if-else statements. Different regular expression patterns for the integer type are created to handle not only decimal values, but also hexadecimal and octadecimal values. In case of an invalid value, an appropriate exception is raised. 

### syntaxer(): 
The syntaxer() function receives the to_syntaxer list as input. Then the function checks the received operating codes and the types attached to them line by line for a match.  First the number of operands is checked, and then their types. The list of operating codes and operands is stored in the opcode_operands dictionary defined inside the function. To handle an operand of type < symb >, a symb_def list was created containing all the token types included in it. 

### genXML(): 
The genXML() function receives a list of lexer_out as input. It simply builds an XML tree using the xml.etree.ElementTree library and prints it to the standard output.