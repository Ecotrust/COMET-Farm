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

### Errors

**Closed linestring**
> 1: points must form a closed linestring for location POLYGON ((-121.022761961 45.5939790921,-121.023137555 45.5939093221,-121.023595258 45.5944688277,-121.025491329 45.5937490181,-121.025591559 45.5940073598,-121.025907727 45.594303344,-121.02596715 45.5939375804,-121.026342741 45.5938677999,-121.026883617 45.5944986659,-121.031367582 45.5948854538,-121.031852345 45.5956136919,-121.031295399 45.5958302507,-121.03034909 45.5965563821,-121.028966953 45.5970938204,-121.02874832 45.5973776001,-121.030610589 45.5974986768,-121.031863025 45.5963636309,-121.031852345 45.5956136919,-121.032959482 45.5958055396,-121.033680214 45.596457734,-121.035642586 45.5966269298,-121.035653076 45.5975909957,-121.034823744 45.5971565771,-121.033692398 45.5976937161,-121.0341018 45.5978446946,-121.035351728 45.5979523768,-121.033450861 45.5982426404,-121.032537806 45.598062597,-121.031862712 45.5982645974,-121.030528467 45.5981625374,-121.029764968 45.5983910943,-121.028046884 45.5982595747,-121.027207554 45.5977485279,-121.026794408 45.5971074499,-121.028341233 45.596686309,-121.029931325 45.5954282341,-121.029316407 45.5952511955,-121.028314779 45.5960192321,-121.02702366 45.5964861806,-121.026118072 45.596402211,-121.025576007 45.5955879097,-121.023090943 45.5963313839,-121.022812517 45.5961853888,-121.022318867 45.5955666961,-121.022763517 45.5952065997,-121.022321656 45.5946250799,-121.022580593 45.5941258385,-121.022761961 45.5939790921,-121.025516657 45.5948521635,-121.025200487 45.5945561783,-121.025141059 45.5949219417,-121.024717605 45.595095409,-121.025134519 45.5952608401,-121.025141059 45.5949219417,-121.025516657 45.5948521635,-121.02576761 45.5951432249,-121.026008724 45.5948555461,-121.025516657 45.5948521635,-121.024014261 45.5951312688,-121.024265208 45.5954223339,-121.02450633 45.5951346579,-121.024014261 45.5951312688))

*fix*: make sure first coordinate pair and last coord pair matches
