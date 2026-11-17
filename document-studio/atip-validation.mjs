// Source-specific preparation checks. This does not submit, sign or certify a prescribed form.
export function validateATIP(document,issue){
 const root=document.payload;if(root.kind!=='material_privacy_breach')return;
 const at=parts=>parts.reduce((v,k)=>v?.[k],root),full=parts=>['payload',...parts];
 const populated=v=>v&&typeof v==='object'?Boolean(v.en?.trim()&&v.fr?.trim()):typeof v==='string'?Boolean(v.trim()):Boolean(v);
 const need=(parts,message='Complete this report field in the required language(s) / Compléter ce champ du rapport dans les langues requises.')=>{if(!populated(at(parts)))issue(full(parts),'breachRequired',message);};
 const type=root.report?.ReportState;
 need(['report','ReportState']);
 if(type==='ReportState-2'){
  need(['report','OPCFileNumber']);need(['amendment_summary'],'Summarize the amendment in English and French / Résumer la modification en anglais et en français.');return;
 }
 if(type!=='ReportState-1')return;
 need(['report','InstitutionRefNumber']);
 if(!populated(root.institution?.InstitutionName)&&!populated(root.institution?.InstitutionNameOther))need(['institution','InstitutionName']);
 for(const field of ['InstitutionCoordinatorName','InstitutionCoordinatorTelephone','InstitutionCoordinatorEmail','Representative','InstitutionContactName','InstitutionContactTitle','InstitutionContactTelephone','InstitutionContactEmail'])need(['institution',field]);
 for(const field of ['BreachDateStart','BreachDateDiscovered'])need(['timeline',field]);
 for(const field of ['BreachType','BreachCause'])need(['type_cause',field]);
 if(root.type_cause?.BreachType==='BreachType-5')need(['type_cause','BreachTypeOther']);
 if(['BreachCause-4','BreachCause-11','BreachCause-13','BreachCause-17','BreachCause-35'].includes(root.type_cause?.BreachCause))need(['type_cause','BreachCauseComment']);
 for(const field of ['BreachOccurenceDescription','OrganizationIdentification','LocationIdentification','BreachDiscoveryDescription','ReleventSystemsIdentification','ReleventServicesIdentification','UnauthorizedRecipientDescription','PartiesRelationship'])need(['description',field]);
 need(['safeguards','SecuritySafeguard']);
 if(root.safeguards?.SecuritySafeguard==='SecuritySafeguard-1'&&!['SecuritySafeguardAdministrative','SecuritySafeguardPhysical','SecuritySafeguardTechnical'].some(k=>root.safeguards[k]))issue(full(['safeguards']),'breachChoice','Identify the safeguard types / Indiquer les types de mesures de protection.');
 if(root.safeguards?.TechnicalSafeguardOther)need(['safeguards','TechnicalSafeguardOtherComment']);
 const personal=root.personal_information||{};
 if(!['PersonalInfoAboutClient','PersonalInfoAboutFederalEmployee','PersonalInfoAboutOther','PersonalInfoAboutUnknown'].some(k=>personal[k]))issue(full(['personal_information']),'breachChoice','Indicate who the information concerned / Indiquer les personnes concernées par les renseignements.');
 if(personal.PersonalInfoAboutOther)need(['personal_information','PersonalInfoAboutOtherComment']);if(personal.PersonalInfoAboutUnknown)need(['personal_information','PersonalInfoAboutUnknownComment']);
 const categories={PersonalInfoCategoryAccount:'AccountDescription',PersonalInfoCategoryIdentifyingNumber:'IdentifyingNumberDescription',PersonalInfoCategoryBiometric:'BiometricDescription',PersonalInfoCategoryContact:'ContactDescription',PersonalInfoCategoryCredential:'CredentialDescription',PersonalInfoCategoryDemographic:'DemographicDescription',PersonalInfoCategoryEducation:'EducationDescription',PersonalInfoCategoryEmployment:'EmploymentDescription',PersonalInfoCategoryFinancial:'FinancialDescription',PersonalInfoCategoryGenetic:'GeneticDescription',PersonalInfoCategoryGovernmentIssued:'GovernmentIssuedDescription',PersonalInfoCategoryHealth:'HealthDescription',PersonalInfoCategoryLaw:'LawDescription',PersonalInfoCategoryLocation:'LocationDescription',PersonalInfoCategoryOtherPreference:'OtherPreferenceDescription',PersonalInfoCategorySecurity:'SecurityDescription',PersonalInfoCategoryOther:'PersonalInfoOtherDescription'};
 for(const[key,description]of Object.entries(categories))if(personal[key])need(['personal_information',description]);
 if(!Object.keys(categories).some(k=>personal[k]))need(['personal_information','PersonalInfoCategoryComment'],'Describe the categories known, or explain that they are unknown / Décrire les catégories connues ou expliquer qu’elles sont inconnues.');
 if(personal.PersonalInfoCategoryOther)need(['personal_information','PersonalInfoCategoryOtherComment']);
 need(['pibs','IncludedInPersonalInformationBank']);if(root.pibs?.IncludedInPersonalInformationBank==='IncludedInPersonalInformationBank-1')need(['pibs','InstitutionPibNumber']);
 if(!Object.entries(root.risk||{}).some(([key,value])=>key.startsWith('Risk')&&value===true))issue(full(['risk']),'breachChoice','Identify the anticipated significant harms / Indiquer les préjudices graves prévus.');
 need(['risk','InstitutionAnticipatedRiskDescription']);
 for(const field of ['NotifiedAffectedIndividuals','NotificationMethod'])need(['notification',field]);
 if(root.notification?.NotifiedAffectedIndividuals==='NotifiedAffectedIndividuals-1'){need(['notification','NotificationStartDate']);need(['notification','NotificationStartDateStatus']);}
 if(root.notification?.NotifiedAffectedIndividuals==='NotifiedAffectedIndividuals-2'||root.notification?.NotificationMethod==='NotificationMethod-4')need(['notification','NotNotifiedReason']);
 for(const field of ['InstitutionIdentifiedUnauthRecipient','CompromisedInformationAccessible','IndividualRiskMitigationDescription'])need(['containment',field]);
 if(root.containment?.InstitutionIdentifiedUnauthRecipient==='InstitutionIdentifiedUnauthRecipient-1')need(['containment','InstitutionContactedRecipient']);
 need(['prevention','BreachRiskMitigationDescription']);need(['submission','SubmitSelectOne']);
 const start=root.timeline?.BreachDateStart,discovered=root.timeline?.BreachDateDiscovered;if(start&&discovered&&start>discovered)issue(full(['timeline','BreachDateDiscovered']),'dateOrder','Discovery date precedes the stated start date / La date de découverte précède la date de début indiquée.');
}
