import json
import logging
import xml.etree.ElementTree as ET
import ezid
import sys
import datetime

class identifierBuilder:

	__root = None
	
	def __init__(self):		
		pass

	# transfer json format into xml format
	def buildXML(self, metadata):				
		self.initialHeader()

		# mandatory
		self.setIdentifier(metadata)
		self.setCreators(metadata)
		self.setTitles(metadata)
		self.setPublisher(metadata)
		self.setPublicationYear(metadata)

		# required
		self.setSubjects(metadata)
		self.setContributors(metadata)
		self.setDates(metadata)
		self.setResourceType(metadata)			
		self.setRelatedIdentifiers(metadata)
		self.setAlternateIdentifiers(metadata)						
		self.setDescription(metadata)
		self.setGeoLocatons(metadata)

		# optional
		self.setRightsList(metadata)
		self.setSizes(metadata)
		self.setFormats(metadata)
		self.setVersion(metadata)

	def getXML(self):			
		if self.__root != None:
			return self.__root
		else:
			print 'XML object is not defined!'					

	def initialHeader(self):		
		self.__root = ET.Element("resource")
		self.__root.attrib['xmlns'] = "http://datacite.org/schema/kernel-3"
		self.__root.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
		self.__root.attrib['xsi:schemaLocation'] = "http://datacite.org/schema/kernel-3 http://schema.datacite.org/meta/kernel-3/metadata.xsd"

	# mandatory	
	def setIdentifier(self, metadata):								
		identifier = ET.SubElement(self.__root, 'identifier')
		identifier.attrib['identifierType'] = 'DOI'
		identifier.text = "(:tba)"		

	# mandatory
	def setCreators(self, metadata):
		if 'creators' in metadata:
			creators = ET.SubElement(self.__root, 'creators')
			for elem in metadata['creators']:
				creator = ET.SubElement(creators, 'creator')
				creatorName = ET.SubElement(creator, 'creatorName')
				if elem['creatorName']['text'] != None:			
					creatorName.text = elem['creatorName']['text']
				else:
					raise ValueError('Error: creator name is null!')

				if 'nameIdentifier' in elem:
					nameIdentifier = ET.SubElement(creator, 'nameIdentifier')
					nameIdentifier.attrib['schemeURI'] = elem['nameIdentifier'].get('schemeURI','')
					nameIdentifier.attrib['nameIdentifierScheme'] = elem['nameIdentifier'].get('nameIdentifierScheme','')
					nameIdentifier.text = elem['nameIdentifier'].get('text','(:unas)')

				if 'affiliation' in elem:
					affiliation = ET.SubElement(creator, 'affiliation')
					affiliation.text = elem['affiliation'].get('text', '(:unas)')
		else:
			raise ValueError('Error: creator is empty!')			

	# mandatory
	def setTitles(self, metadata):
		if 'titles' in metadata:
			titles = ET.SubElement(self.__root, 'titles')
			for elem in metadata['titles']:
				title = ET.SubElement(titles, 'title')				
				title.attrib['xml:lang'] = elem.get('xml:lang', 'en-us')
				title.text = elem['text']
		else:
			raise ValueError('Error: title is empty!')			

	# mandatory
	def setPublisher(self, metadata):
		if 'publisher' in metadata:
			publisher = ET.SubElement(self.__root, 'publisher')
			publisher.text = metadata['publisher']['text']
		else:
			publisher = ET.SubElement(self.__root, 'publisher')
			publisher.text = 'CyVerse Data Commons'			

	# mandatory
	def setPublicationYear(self, metadata):
		if 'publicationYear' in metadata:
			publicationYear = ET.SubElement(self.__root, 'publicationYear')
			publicationYear.text = metadata['publicationYear']['text']
		else:
			publicationYear = ET.SubElement(self.__root, 'publicationYear')
			now = datetime.datetime.now()
			publicationYear.text = str(now.year)
	
	# required			
	def setSubjects(self, metadata):
		if 'subjects' in metadata:
			subjects = ET.SubElement(self.__root, 'subjects')
			for elem in metadata['subjects']:
				subject = ET.SubElement(subjects, 'subject')			
				subject.text = elem['text']
				subject.attrib['xml:lang'] = elem.get('xml:lang','en-us')										
				subject.attrib['schemeURI'] = elem.get('schemeURI','')				
				subject.attrib['subjectScheme'] = elem.get('subjectScheme','')
		else:
			pass

	def setContributors(self, metadata):
		if 'contributors' in metadata:
			contributors = ET.SubElement(self.__root, 'contributors')
			for elem in metadata['contributors']:				
				contributor = ET.SubElement(contributors, 'contributor')
				contributor.attrib['contributorType'] = elem.get('contributorType','Other')
				
				if 'contributorName' in elem:
					contributorName = ET.SubElement(contributor, 'contributorName')
					contributorName.text = elem['contributorName'].get('text', '')

				if 'nameIdentifier' in elem:
					nameIdentifier = ET.SubElement(contributor, 'nameIdentifier')					
					nameIdentifier.attrib['schemeURI'] = elem['nameIdentifier'].get('schemeURI', '')					
					nameIdentifier.attrib['nameIdentifierScheme'] = elem['nameIdentifier'].get('nameIdentifierScheme', '')
					nameIdentifier.text = elem['nameIdentifier'].get('text', '(:unas)')

				if 'affiliation' in elem:
					affiliation = ET.SubElement(contributor, 'affiliation')
					affiliation.text = elem['affiliation'].get('text', '(:unas)')
		else:
			pass

	def setDates(self, metadata):
		if 'dates' in metadata:
			dates = ET.SubElement(self.__root, 'dates')
			for elem in metadata['dates']:
				date = ET.SubElement(dates, 'date')			
				date.attrib['dateType'] = elem.get('dateType', '')
				date.text = elem['text']
		else:
			pass

	def setAlternateIdentifiers(self, metadata):
		if 'alternateIdentifiers' in metadata:
			alternateIdentifiers = ET.SubElement(self.__root, 'alternateIdentifiers')
			for elem in metadata['alternateIdentifiers']:
				alternateIdentifier = ET.SubElement(alternateIdentifiers, 'alternateIdentifier')
				alternateIdentifier.attrib['alternateIdentifierType'] = elem.get('alternateIdentifierType', '')
				alternateIdentifier.text = elem.get('text', '(:unas)')
		else:
			pass

	def setRelatedIdentifiers(self, metadata):
		if 'relatedIdentifiers' in metadata:
			relatedIdentifiers = ET.SubElement(self.__root, 'relatedIdentifiers')	
			for elem in metadata['relatedIdentifiers']:
				relatedIdentifier = ET.SubElement(relatedIdentifiers, 'relatedIdentifier')
				relatedIdentifier.attrib['relatedIdentifierType'] = elem.get('relatedIdentifierType', '')
				relatedIdentifier.attrib['relationType'] = elem.get('relationType', '')
				relatedIdentifier.attrib['relatedMetadataScheme'] = elem.get('relatedMetadataScheme', '')
				relatedIdentifier.attrib['schemeURI'] = elem.get('schemeURI', '')
				relatedIdentifier.text = elem.get('text', '(:unas)')
		else:			
			pass

	def setResourceType(self, metadata):
		if 'resourceType' in metadata:
			resourceType = ET.SubElement(self.__root, 'resourceType')
			resourceType.attrib['resourceTypeGeneral'] = metadata['resourceType'].get('resourceTypeGeneral', 'Dataset')			
			resourceType.text = metadata['resourceType']['text']			
		else:
			pass

	def setSizes(self, metadata):
		if 'sizes' in metadata:
			sizes = ET.SubElement(self.__root, 'sizes')
			for elem in metadata['sizes']:
				size = ET.SubElement(sizes, 'size')
				size.text = elem['text']
		else:
			pass

	def setFormats(self, metadata):
		if 'formats' in metadata:
			formats = ET.SubElement(self.__root, 'formats')
			for elem in metadata['formats']:
				format = ET.SubElement(formats, 'format')			
				format.text = elem['text']
		else:			
			pass

	def setVersion(self, metadata):
		if 'version' in metadata:
			version = ET.SubElement(self.__root, 'version')
			version.text = metadata['version']['text']

	def setRightsList(self, metadata):
		if 'rightsList' in metadata:
			rightList = ET.SubElement(self.__root, 'rightsList')
			for elem in metadata['rightsList']:
				rights = ET.SubElement(rightList, 'rights')
				rights.attrib['rightsURI'] = elem.get('rightsURI', '')
				rights.text = elem['text']
		else:
			pass

	def setDescription(self, metadata):
		if 'descriptions' in metadata:
			descriptions = ET.SubElement(self.__root, 'descriptions')
			for elem in metadata['descriptions']:
				description = ET.SubElement(descriptions, 'description')
				description.attrib['descriptionType'] = elem.get('descriptionType', "Abstract")				
				description.attrib['xml:lang'] = elem.get('xml:lang', 'en-us')
				description.text = elem['text']
		else:
			pass

	def setGeoLocatons(self, metadata):
		if 'geoLocations' in metadata:
			geoLocations = ET.SubElement(self.__root, 'geoLocations')
			for elem in metadata['geoLocations']:
				geoLocation = ET.SubElement(geoLocations, 'geoLocation')
				geoLocationPoint = ET.SubElement(geoLocation, 'geoLocationPoint')
				geoLocationBox = ET.SubElement(geoLocation, 'geoLocationBox')
				geoLocationPlace = ET.SubElement(geoLocation, 'geoLocationPlace')

				geoLocationPoint.text = elem['geoLocationPoint']['text']
				geoLocationBox.text = elem['geoLocationBox']['text']
				geoLocationPlace.text = elem['geoLocationPlace']['text']
		else:
			pass			
		




