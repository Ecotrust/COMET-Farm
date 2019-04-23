Day
  - cometEmailId = user email address registered in COMET-Farm  

Cropland  
  - name = descriptive name of model run  

GEOM  
*WKT parcel or point GIS Definition*
  - SRID = projection id, suggest using NAD83 (4326) 
  - AREA = size in acres of parcel or point
  
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
  

"Intensive Tillage","Reduced Tillage","No Till"

  
 
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
