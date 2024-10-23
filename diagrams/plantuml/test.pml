@startuml
ProvisionFabricEnabledWorkspace --> CreateOrUpdateProfilesYml : " "
CreateOrUpdateProfilesYml --> CreateYourDbtProject : " "
CreateYourDbtProject --> Update : " "
@enduml