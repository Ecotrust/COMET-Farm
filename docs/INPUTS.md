### Applicable to all model runs  

| XML Tag | XML Name | Excel Name | GIS Name | Value |
|---------|----------|------------|----------|-------|
| `<Day>` | `cometEmailId` | `Email` \* | N/A | N/A |
| `<CRP>` | N/A | `CRP` \* |  N/A | `No` |

\* *Will be same across all model runs*  

Day  
`cometEmailId` - user email address registered in COMET-Farm  

___  


### User defined      

| XML Tag | XML Name | Excel Name | GIS Name | Value |
|---------|----------|------------|----------|-------|
| `<Cropland>` | `name` | `Name` | N/A | *user defined* |  


Cropland  
`name` - descriptive name of model run

---  

### GIS generated  

| XML Tag | XML Name | Excel Name | GIS Name | Type |
|---------|----------|------------|----------|-------|
| `<GEOM>` | N/A | `GEOM` | ? | `MultiPolygon`, `Polygon`, `Point` |
| `<GEOM>` | `SRID` | `SRID` | ? | ? |
| `<GEOM>` | `AREA` | `AREA` | `acres` | int |
| `<Pre-1980>` | N/A | `pre_80` | `pre_80` | XML: str, GIS: int (List) |
| `<Year1980-2000>` (str) | N/A | `yr80_2000` | `yr80_2000` (int) | XML: str, GIS: int (List) |
| `<Year1980-2000_Tillage>` (str) | N/A | `till80_200` | `till80_200` (int) | XML: str, GIS: int (List) |
| `<CropScenario>` | NAME | `crop_scenario_name` | `${id}_${<field id>}_${}_${<scenario id>}` ** | string |
| `<CropYear>` | `YEAR` |'YEAR' | N/A | 2000 to the current year - 1 |
| `<Crop>` | `CropNumber` | 'CROP_NUMBER' | COMET_ID? | "1" or "2" (str) |
| `<CropName>` | N/A | `Ccop_name` | `Ccop_name` | string |
| `<PlantingDate>` | N/A | `planting_date` | ? | mm/dd/yyyy |
| `<ContinueFromPreviousYear>` | N/A | `continue_from_previous_year` | ? | "Yes" or "No" (str) |
| `<HarvestDate>` | N/A | `harvest_date` | ? | mm/dd/yyyy |
| `<Grain>` | N/A | `grain` | ? | "Yes" or "No" (str) |
| `<yield>` | N/A | `yield` | ? | List |
| `<StrawStoverHayRemoval>` | N/A | `straw_stover_hay_removal` | ? | Units in % |
| `<TillageDate>` | N/A | `tillage_date` | ? | mm/dd/yyyy |
| `<TillageType>` | N/A | `tillage_type` | ? | List |
| `<NApplicationDate>` | N/A | `n_application_date` | ? | mm/dd/yyyy |
| `<NApplicationType>` | N/A | `n_application_type` | ? | List |
| `<NApplicationAmount>` | N/A | `n_application_amount` | ? | units in lbs N/acre |
| `<NApplicationMethod>` | N/A | `n_application_method` | ? | List |
| `<EEP>` | N/A | `eep` | ? | List |


\*\* *Need clarification of which GIS fields match*


GEOM  
*WKT parcel or point GIS Definition*  
`SRID` - projection id, suggest using NAD83 (4326)  
`AREA` - size in acres of parcel or point
  - example of failed GEOM:  
  ```
  <GEOM PARCELNAME="New" SRID="4326" AREA="58.8717002869">POLYGON ((-121.022761961 45.5939790921,-121.023137555 45.5939093221,-121.023595258 45.5944688277,-121.025491329 45.5937490181,-121.025591559 45.5940073598,-121.025907727 45.594303344,-121.02596715 45.5939375804,-121.026342741 45.5938677999,-121.026883617 45.5944986659,-121.031367582 45.5948854538,-121.031852345 45.5956136919,-121.031295399 45.5958302507,-121.03034909 45.5965563821,-121.028966953 45.5970938204,-121.02874832 45.5973776001,-121.030610589 45.5974986768,-121.031863025 45.5963636309,-121.031852345 45.5956136919,-121.032959482 45.5958055396,-121.033680214 45.596457734,-121.035642586 45.5966269298,-121.035653076 45.5975909957,-121.034823744 45.5971565771,-121.033692398 45.5976937161,-121.0341018 45.5978446946,-121.035351728 45.5979523768,-121.033450861 45.5982426404,-121.032537806 45.598062597,-121.031862712 45.5982645974,-121.030528467 45.5981625374,-121.029764968 45.5983910943,-121.028046884 45.5982595747,-121.027207554 45.5977485279,-121.026794408 45.5971074499,-121.028341233 45.596686309,-121.029931325 45.5954282341,-121.029316407 45.5952511955,-121.028314779 45.5960192321,-121.02702366 45.5964861806,-121.026118072 45.596402211,-121.025576007 45.5955879097,-121.023090943 45.5963313839,-121.022812517 45.5961853888,-121.022318867 45.5955666961,-121.022763517 45.5952065997,-121.022321656 45.5946250799,-121.022580593 45.5941258385,-121.022761961 45.5939790921,-121.025516657 45.5948521635,-121.025200487 45.5945561783,-121.025141059 45.5949219417,-121.024717605 45.595095409,-121.025134519 45.5952608401,-121.025141059 45.5949219417,-121.025516657 45.5948521635,-121.02576761 45.5951432249,-121.026008724 45.5948555461,-121.025516657 45.5948521635,-121.024014261 45.5951312688,-121.024265208 45.5954223339,-121.02450633 45.5951346579,-121.024014261 45.5951312688))</GEOM>
  ```

Pre-1980  
*one of the following options:*   
  - [ ] "Irrigation (Pre 1980s)"
  - [ ] "Livestock Grazing"
  - [ ] "Lowland Non-Irrigated Pre-1980s"
  - [ ] "Upland Non-irrigated Pre-1980s"

CRP  
*one of the following options:*
  - [ ] "No"
  - [ ] "Yes"

CRPStartYear  
*yyyy* (Must be in yyyy)

CRPEndYear
*yyyy* (Must be in yyyy)  

CRPType  
*one of the following options:*
  - [ ] "100% Grass"
  - [ ] "Grass/Legume Mixture"  

PreCRPManagement  
*one of the following options:*  
  - [ ] "Irrigated: Annual Crops in Rotation"
  - [ ] "Irrigated: Annual Crops with Hay/Pasture in Rotation"
  - [ ] "Irrigated: Continuous Hay"
  - [ ] "Irrigated: Orchard or Vineyard"
  - [ ] "Non-Irrigated: Annual Crops in Rotation"
  - [ ] "Non-Irrigated: Continuous Hay"
  - [ ] "Non-Irrigated: Livestock Grazing"
  - [ ] "Non-Irrigated: Fallow-Grain"
  - [ ] "Non-Irrigated: Orchard or Vineyard"

PreCRPTillage  
*one of the following options:*  
  - [ ] "Intensive Tillage"
  - [ ] "Reduced Tillage"
  - [ ] "No Till"

PostCRPManagement  
*one of the following options:*  
  - [ ] "Irrigated: Annual Crops in Rotation"
  - [ ] "Irrigated: Annual Crops with Hay/Pasture in Rotation"
  - [ ] "Irrigated: Continuous Hay"
  - [ ] "Irrigated: Orchard or Vineyard"
  - [ ] "Non-Irrigated: Annual Crops in Rotation"
  - [ ] "Non-Irrigated: Continuous Hay"
  - [ ] "Non-Irrigated: Livestock Grazing"
  - [ ] "Non-Irrigated: Fallow-Grain"
  - [ ] "Non-Irrigated: Orchard or Vineyard"

PostCRPTillage  
*one of the following options:*  
  - [ ] "Intensive Tillage"
  - [ ] "Reduced Tillage"
  - [ ] "No Till"  

Year1980-2000
*one of the following options:*  
  - [ ] "Irrigated: Annual Crops in Rotation"
  - [ ] "Irrigated: Annual Crops with Hay/Pasture in Rotation"
  - [ ] "Irrigated: Continuous Hay"
  - [ ] "Irrigated: Orchard or Vineyard"
  - [ ] "Non-Irrigated: Annual Crops in Rotation"
  - [ ] "Non-Irrigated: Continuous Hay"
  - [ ] "Non-Irrigated: Livestock Grazing"
  - [ ] "Non-Irrigated: Fallow-Grain"
  - [ ] "Non-Irrigated: Orchard or Vineyard"

Year1980-2000_Tillage  
*one of the following options:*  
  - [ ] "Intensive Tillage"
  - [ ] "Reduced Tillage"
  - [ ] "No Till"

CropScenario  
`Name` - crop scenario name  

CropYear  
`Year` - yyyy format  
CropYear definitions repeat for each year from 2000 to the current calendar year - 1

---  

Crop  
`CropNumber` - option is "1" or "2"  

CropName  
*one of the following options:*  
  - [ ] "Alfalfa"
  - [ ] "Barley"
  - [ ] "Broccoli-Coast"
  - [ ] "Broccoli-Desert"
  - [ ] "Cauliflower"
  - [ ] "Clover"
  - [ ] "Corn"
  - [ ] "Corn Silage"
  - [ ] "Cotton"
  - [ ] "Dry Field Beans"
  - [ ] "Fallow"
  - [ ] "Grass"
  - [ ] "Grass-Legume Mix"
  - [ ] "Lettuce-Head"
  - [ ] "Lettuce-Romaine"
  - [ ] "Lettuce-Leaf"
  - [ ] "Millet"
  - [ ] "Oats"
  - [ ] "Peanut"
  - [ ] "Potato"
  - [ ] "Rice - Flooded"
  - [ ] "Rye"
  - [ ] "Sorghum"
  - [ ] "Sorghum Silage"
  - [ ] "Soybean"
  - [ ] "Spring Wheat"
  - [ ] "Strawberry"
  - [ ] "Sugar Beets"
  - [ ] "Sunflower"
  - [ ] "Switchgrass"
  - [ ] "Tomatoes, Fresh"
  - [ ] "Tomatoes, Processing"
  - [ ] "Winter Wheat"
  - [ ] "Annual Rye - Legume - Radish"
  - [ ] "Annual Rye - Legume"
  - [ ] "Annual Rye"
  - [ ] "Cereal Rye"
  - [ ] "Clover"
  - [ ] "Corn"
  - [ ] "Forage Radish"
  - [ ] "Millet"
  - [ ] "Oilseed Radish"
  - [ ] "Winter Grain-Other"
  - [ ] "Sorghum"
  - [ ] "Vetch"
  - [ ] "Winter Wheat"
  - [ ] "Almond"
  - [ ] "Grape, Raisin"
  - [ ] "Grape, Table"
  - [ ] "Grape, Wine (<1390 GDD)"
  - [ ] "Grape, Wine (1391-1670 GDD)"
  - [ ] "Grape, Wine (1671-1950 GDD)"
  - [ ] "Grape, Wine (>1950 GDD)"
  - [ ] "Grapefruit"
  - [ ] "Lemons & Limes"
  - [ ] "Oranges"
  - [ ] "Pistachio"
  - [ ] "Tangerines & Mandarins"
  - [ ] "English Walnuts"

PlantingDate  
Date must be in mm/dd/yyyy format  

ContinueFromPreviousYear
*one of the following options:*
  - [ ] "No"
  - [ ] "Yes"

DidYouPrune  
*one of the following options:*
  - [ ] "No"
  - [ ] "Yes"

RenewOrClearYourOrchard  
*one of the following options:*
  - [ ] "No"
  - [ ] "Yes"

HarvestList  

HarvestEvent  

HarvestDate  
Date must be in mm/dd/yyyy format  

Grain  
*one of the following options:*
  - [ ] "No"
  - [ ] "Yes"

yield  
Refer to "Units" worksheet for details on units (?)

StrawStoverHayRemoval  
Units in %  

GrazingList

TillageList

TillageEvent  

TillageDate  
Date must be in mm/dd/yyyy format  

TillageType  
*one of the following options:*  
  - [ ] "Intensive Tillage"
  - [ ] "Reduced Tillage"
  - [ ] "Mulch Tillage"
  - [ ] "Ridge Tillage"
  - [ ] "Strip Tillage"
  - [ ] "No Tillage"
  - [ ] "Growing Season Cultivation"
  - [ ] "Mow"
  - [ ] "Crimp"
  - [ ] "Broad-spectrum herbicide"  

NApplicationList  

NApplicationEvent  

NApplicationDate  
Date must be in mm/dd/yyyy format  

NApplicationType  
*one of the following options:*  
  - [ ] "Ammonium Nitrate"
  - [ ] "Anhydrous Ammonia"
  - [ ] "Ammonium Sulfate"
  - [ ] "Urea"
  - [ ] "UAN"
  - [ ] "Compost"
  - [ ] "Mixed Blends"
  - [ ] "Mono-Ammonium Phosphate"
  - [ ] "Di-Ammonium Phosphate"

NApplicationAmount
Units in lbs N/acre  

NApplicationMethod  
*one of the following options:*  
  - [ ] "Surface Broadcast"
  - [ ] "Surface Band / Sidedress"
  - [ ] "Incorporate / Inject"
  - [ ] "Fertigation"
  - [ ] "Aerial Application"

EEP  
*one of the following options:*  
  - [ ] "None"
  - [ ] "Slow Release"
  - [ ] "Nitrification Inhibitor"

OMADApplicationList  

OMADApplicationEvent

OMADApplicationDate
Date must be in mm/dd/yyyy format  

OMADType  
*one of the following options:*  
  - [ ] "Compost or Composted Manure"
  - [ ] "Farmyard Manure"
  - [ ] "Other"
  - [ ] "Beef"
  - [ ] "Dairy"
  - [ ] "Chicken - Broiler (litter)"
  - [ ] "Chicken - layer"
  - [ ] "Sheep"
  - [ ] "Swine"  

OMADApplicationAmount  
Units in tons dry matter per acre

OMADPercentN  
Units in % N  

OMADCNRatio

IrrigationList

IrrigationApplicationEvent

IrrigationApplicationDate
IrrigationApplicationAmount

IrrigationApplicationAmount
Units in inches


LimingList

LimingApplicationEvent

LimingApplicationDate
Date must be in mm/dd/yyyy format

LimingMaterial
*one of the following options:*  
  - [ ] "None"
  - [ ] "Crushed Limestone"
  - [ ] "Calcitic Limestone"
  - [ ] "Dolomitic Limestone"

LimingApplicationAmount
Units in tons/acre

BurningList

BurningEvent

DidYouBurnCropResidue
*one of the following options:*  
  - [ ] "No burning"
  - [ ] "Yes, before planting"
  - [ ] "Yes, after harvesting"

---  

:repeat: `<Crop>`

:note: Options are exactly as above for crop #1 for this year. Planting date cannot be earlier than the harvest date of the previous crop.

:note: None of the other events (tillage, Napplication, OMADapplication, etc.) can have dates prior to the last harvest date of crop #1 of the previous year.


## XML Scheme

```xml
<Day cometEmailId="<user email address registered in COMET-Farm">
  <Cropland name="<descriptive name of model run">
    <GEOM SRID="<SRID of projection - suggest using NAD83 (4326)>" AREA="<size in acres of parcel or point>">WKT parcel or point GIS Definition</GEOM>
    <Pre-1980>Upland Non-Irrigated (Pre 1980s)</Pre-1980>
    <CRP>None</CRP>
    <CRPStartYear></CRPStartYear>
    <CRPEndYear></CRPEndYear>
    <CRPType>None</CRPType>
    <PreCRPManagement></PreCRPManagement>
    <PreCRPTillage></PreCRPTillage>
    <PostCRPManagement></PostCRPManagement>
    <PostCRPTillage></PostCRPTillage>
    <Year1980-2000>Non-Irrigated: Corn-Soybean</Year1980-2000>
    <Year1980-2000_Tillage>Intensive Tillage</Year1980-2000_Tillage>
    <CropScenario Name="Current">
      <CropYear Year="2000">
        <Crop CropNumber="1">
          <CropName>corn</CropName>
          <PlantingDate>05/07/2000</PlantingDate>
          <ContinueFromPreviousYear>N</ContinueFromPreviousYear>
          <DidYouPrune></DidYouPrune>
          <RenewOrClearYourOrchard/Vinyard></RenewOrClearYourOrchard/Vinyard>
          <HarvestList>
            <HarvestEvent>
              <HarvestDate>10/23/2000</HarvestDate>
              <Grain>Yes</Grain>
              <yield>167.0</yield>
              <StrawStoverHayRemoval>0</StrawStoverHayRemoval>
            </HarvestEvent>
          </HarvestList>
          <GrazingList>
          </GrazingList>
          <TillageList>
            <TillageEvent>
              <TillageDate>05/06/2000</TillageDate>
              <TillageType>Intensive Tillage</TillageType>
            </TillageEvent>
          </TillageList>
          <NApplicationList>
            <NApplicationEvent>
              <NApplicationDate>05/07/2000</NApplicationDate>
              <NApplicationType>UAN</NApplicationType>
              <NApplicationAmount>116.4</NApplicationAmount>
              <NApplicationMethod>Surface Band / Sidedress</NApplicationMethod>
              <EEP>None</EEP>
            </NApplicationEvent>
          </NApplicationList>
          <OMADApplicationList>
            <OMADApplicationEvent>
              <OMADApplicationDate></OMADApplicationDate>
              <OMADType></OMADType>
              <OMADApplicationAmount></OMADApplicationAmount>
              <OMADPercentN></OMADPercentN>
              <OMADCNRatio></OMADCNRatio>
            </OMADApplicationEvent>
          </OMADApplicationList>
          <IrrigationList>
            <IrrigationApplicationEvent>
              <IrrigationApplicationDate></IrrigationApplicationDate>
              <IrrigationApplicationAmount></IrrigationApplicationAmount>
            </IrrigationApplicationEvent>
          </IrrigationList>
          <LimingList>
            <LimingApplicationEvent>
              <LimingApplicationDate></LimingApplicationDate>
              <LimingMaterial></LimingMaterial>
              <LimingApplicationAmount></LimingApplicationAmount>
            </LimingApplicationEvent>
          </LimingList>
          <BurningList>
            <BurningEvent>
              <DidYouBurnCropResidue>No Burning</DidYouBurnCropResidue>
            </BurningEvent>
          </BurningList>
        </Crop>
        <Crop CropNumber="2">
        </Crop>
      </CropYear>
      <CropYear definitions repeat for each year from 2000 to the current calendar year - 1>
      </CropYear>
    </CropScenario>
  </Cropland>
</Day>

```
