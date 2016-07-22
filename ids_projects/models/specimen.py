from base_metadata import BaseMetadata


class Specimen(BaseMetadata):
    """ """
    name = 'idsvc.specimen'

    def __init__(self, *args, **kwargs):
        """
        Required Parameter:
            api_client      # AgavePy client
        Optional Parameters:
            uuid            # unique identifier for existing metadata object
            body            # information held in metadata 'value' field
            meta            # json or dictionary, values may include:
                            #   uuid, owner, schemaId, internalUsername,
                            #   associationIds, lastUpdated, name, value,
                            #   created, _links
        Explicit parameters take precedence over values found in the meta dictionary
        """
        super(Specimen, self).__init__(*args, **kwargs)

    @property
    def title(self):
        not_applicable = ('NA', 'N/A', 'NOT APPLICABLE', 'NONE', 'NULL')

        specimen_id = self.value.get('specimen_id')
        if specimen_id.upper() in not_applicable:
            specimen_id = None

        taxon_name = self.value.get('taxon_name')
        if taxon_name.upper() in not_applicable:
            taxon_name = None

        organ_or_tissue = self.value.get('organ_or_tissue')
        if organ_or_tissue.upper() in not_applicable:
            organ_or_tissue = None

        title = specimen_id if specimen_id else ''
        title += ' ' + taxon_name if taxon_name and taxon_name != specimen_id else ''
        title += ' ' + organ_or_tissue if organ_or_tissue and organ_or_tissue not in (specimen_id, taxon_name) else ''

        return title

    @property
    def project(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.project']), None)

    @property
    def processes(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.process']

    @property
    def data(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.data']
