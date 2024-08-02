- Create a class autotrader; constructor takes as input a ticker symbol. Then starts a thread, that always loop through a method called "event loop".

- The event loop should run on a separate thread from the main application that istantiated the object (is this doable? Is it a good practice? Or it's better that in the main application we istantiate a thread for each object we want to istantiate?)

- In the event loop (in whichever way we implement it), which is basically a while true, we do the following:
	- in the first run, take historical data (ex. 10 days previous)

	- take the current value of the stock, append it to data; u need actually to append all the missing data, since the last call to this function. With which interval are we sampling? 
	- call the function which implement the strategy to apply. The string that encode the strategy to apply will be passed to the constructor, with the ticker symbol. For ex MA_XX_YY implement moving averages with XX and YY samples. This function returns a tuple of type (buy, sell) which are boolean values. For ex if (buy, sell) = (True, False) it means a signal to buy is generated. If both are false, do nothing.
	- If buy/sell signal is generated, send notification
	- save data to disk if needed. Data comprend both the curve, and the selling/buy points signaled
	- unload from ram the data that we dont need anymore (that is, the first data that aren't needed anymore to compute the moving averages; this btw should be done in the method that implement the strategy)
	- wait small amount (to not overload cpu)
	- repeat cycle


WHAT WE NEED:
- A CLASS TO IMPLEMENT THE DATA STRUCTURE THAT CONTAIN CURVE, BUY/SELLING POINT, THAT CONTAIN THE PATH OF DATAFILE ON DISK, AND CONTAIN A VARIABLE DATA_RAM THAT CONTAIN ONLY THE DATA NEEDED TO PERFORM COMPUTATION. A KINDA OF BUFFER. ONCE WE DONT NEED DATA ANYMORE, AS TIME PASSES, WE UNLOAD THE REST INTO THE DISK FILE
THE CLASS ALSO KEEP TRACK OF THE LAST TIME WE BOUGHT/SELL

- A value from 1 to 100 must tell us "How strong" is the signal; how much confident the software is that this is a good buy or sell signal