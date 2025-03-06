# WhatsApp summarizer
takes in exported messages from whatsapp, splits them into blocks (while ensuring to not break single conversation chain) and then asks ollama to summarize it (few methods of summarizatino available)  

## options
* n_blocks - number of blocks to divide chat into
* min_gap_min - minimum time gap between blocks in minutes (to not split in the middle of a conversation)
* summary style = 
  *     summarize_all - summarize all blocks together
  *     oneblock_chain - for each block create summary of block and previous summary
  *     simple_chain - generate summary for each block separately only feeding previous summary
  *     double_layer - first generate simple_chain, then summarize it
  *     isolated_chain - generate summary for each block separately without feeding previous summary
  *     isolated_double_layer - generate isolated_chain, then summarize it


## default mode
in default mode the program will try to summarize the entire chat

## question mode
to enter question mode run program with `-q` flag or `q` parameter  
in question mode user can pass custom question (about information from chat history) that will be asked to llm, in order to try and get the answer from the chat history
