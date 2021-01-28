library(wtss)
library(zoo) #for merge.zoo

##########################
# Disclaimer
##########################
# This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the National Institute for Space Research (INPE). No warranty, expressed or implied, is made by the INPE or the Brazil Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the INPE nor the Brazil Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.

#########################
# Licence
#########################
# MIT License
# Copyright (c) 2019 Rodrigues et al.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


server <- wtss::WTSS("http://www.esensing.dpi.inpe.br/wtss/")
#coverages <- wtss::listCoverages(server)
#print(coverages)

cv <- wtss::describeCoverage(server, "MOD13Q1")
#cv$MOD13Q1$description  
#print(cv$MOD13Q1$attributes)


for (veg_ind in c("ndvi","evi") ) {

    scale <- cv$MOD13Q1$attributes$scale_factor[match(veg_ind,cv$MOD13Q1$attributes$name)]
    missing_value <- cv$MOD13Q1$attributes$missing_value[match(veg_ind,cv$MOD13Q1$attributes$name)]

    sourcefile = "./csv/LC8_pivots_middlepoints_coords.csv"

    # Middlepoint in main cardinal directions of center pivots. Header (ObjectID,Lon,Lat), attention these names used below:
    df <- read.csv(file = sourcefile, header = TRUE, sep = ",")

    # Filename output:
    destfile = paste("./csv/LC8_pivots_middlepoints_", veg_ind, "_TS.csv", sep="")

    starts = 1

    if(file.exists(destfile)){
        cat('Reading file of vegetation time series...\n')
        atco <- read.zoo(destfile, sep = ",", header=TRUE, index.column = 1, format="%Y-%m-%d", check.names=FALSE)
    
        if (dim(atco)[2] != dim(df)[1]){
            cat('This file has partial results of vegetation time serie:\n --> ',destfile,'  [Number of samples registered: ',dim(atco)[2],']\n\n')
            cat('Source file to retrieve time series -> ',sourcefile,'  [Number of target samples:',dim(df)[1],']\n\n') 
            res <- system("read -p 'Do you want use this source file to complete partial results (y), (n) to replace partial results with all new retrieve series (y/n/quit): ' input; echo $input", intern = TRUE)
            if (tolower(res) == 'y')
                starts = dim(atco)[2] + 1
            else if (tolower(res) == 'n')
                rm(atco)
            else {
                if (res != 'quit')
                    cat('Invalid option!\n')
                quit('no',1,FALSE)
            }            
        } else{
            cat('There is already a time series file results of this vegetation index:\n',destfile,'\n\n')
            cat('It have the same number of samples defined in the source file:\n',sourcefile,'\n')
            res <- system("read -p 'Do you want replace this time series file (y/n): ' input; echo $input", intern = TRUE)
            if (tolower(res) == 'y')
                cat('Running search at WTSS to replace the file of time series!\n')
            else
                quit('no',1,FALSE)      
        }
     
    }


    for(i in starts:length(df[,1])){
      print(i)
      # Try function to deal with HTTP request failed:
      count <- 0
      repeat {
        if (count == 20) break
        count <- count + 1
        time_series <- try(wtss::timeSeries(server, coverages = "MOD13Q1", attributes=c(veg_ind),
                                  latitude=as.numeric(df$Lat[i]), longitude=as.numeric(df$Lon[i]), start_date="2017-11-01", end_date="2018-04-01"))
        if ('try-error' %in% class(time_series)) next
        else break
      }  
  
      if ('try-error' %in% class(time_series)){
          print('Sorry, persistent error!')
          if (i > 1 ){
              print('Saving partial results, the next execution do you will be asked to complete this task!')

              dir.create('./csv', showWarnings = FALSE)
              # Save partial results:
              write.zoo(atco, file = destfile, index.name = "Date", sep = ",")
          }
          quit('no',1,FALSE)
      }
      else{
          if ( veg_ind == 'ndvi'){
            time_series$MOD13Q1$attributes$ndvi[time_series$MOD13Q1$attributes$ndvi == missing_value]<-NA 
            time_series$MOD13Q1$attributes$ndvi <- time_series$MOD13Q1$attributes$ndvi*scale
          }
          else if ( veg_ind == 'evi'){
            time_series$MOD13Q1$attributes$evi[time_series$MOD13Q1$attributes$evi == missing_value]<-NA 
            time_series$MOD13Q1$attributes$evi <- time_series$MOD13Q1$attributes$evi*scale
          }
          names(time_series$MOD13Q1$attributes) <- i

          if (i > 1)         
             atco <- merge.zoo(atco, time_series$MOD13Q1$attributes)
          else
             atco <- time_series$MOD13Q1$attributes
      }   
    }

    dir.create('./csv', showWarnings = FALSE)
    # Save results:
    write.zoo(atco, file = destfile, index.name = "Date", sep = ",")

}
