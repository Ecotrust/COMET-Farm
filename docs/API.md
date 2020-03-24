#### API State:   :construction:

> Rough development state and there is no polished way of submitting files.


#### API Status: https://comet-farm.com/home/apistatus  

---  

### Usage  

Current method uses a UI site which you could use to upload xml files directly:  
https://comet-farm.com/home/apiview

**Steps**  
  1. Input your cfarm email and select the xml file to upload
      - email needs to be the email of a registered cometfarm user. The finished API run results, inputs and errors will be sent here when the file is done.
      - the uploaded .xml file should have each cropland run be a model run node. The numbers in LastCropland and FirstCropland refer to the order these appear in the file. i.e. LastCropland:10 FirstCropland:5 would mean of the runs in the file, only do the 5th through 10th run. If the LastCropland is negative then the API will run every model run it finds in the file.
      - LastDaycentInput and FirstDaycentInput are for which model runs you would like to receive the daycent inputs that the API built for those locations. These are the schedule files that daycent uses to perform its runs. Leave as 0 to omit returning them or set LastDaycentInput as a very large number to return all inputs.
      - The file key is the actual file being uploaded. In postman this can be set in the Body of the post request in Key Value mode by adding a new key/value of type File, and choosing the input xml file.

  2. The input xml file will be sent to COMET-Farm server to be parsed and added to the API queue

  3. A post request is generated, which you can examine and reverse engineer if you want
      - post request address = https://cometfarm.nrel.colostate.edu///ApiMain/AddToQueue  
      - body
        ```js
          LastCropland:-1
          FirstCropland:-1
          email:EMAIL@EMAIL.COM
          LastDaycentInput:0
          FirstDaycentInput:0
          Files: (type file, value is the uploaded .xml file)
        ```
      - If the post request is successful you will get as a return message:
        ```js
          File successfully added:
          NUM NAME
        ```
        Where "NUM" is the position in the queue of your uploaded file and NAME is the name of the file you uploaded.

  4. When the job is done the results will be emailed to your cometfarm email in .xz format (mislabeled as .lzma, in any case 7zip will be able to open and extract the results)
