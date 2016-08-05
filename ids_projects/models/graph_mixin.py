import logging
import time

logger = logging.getLogger(__name__)


class GraphMixin(object):
    """"""
    @property
    def graph(self):
        start = time.time()
        if self._graph is None:
            self.construct_graph()

        logger.debug("name: {}, graph time: {}".format(self.name, (time.time() - start)))
        return self._graph

    def construct_graph(self):
        """"""
        self._graph = []
        specimens = []
        processes = []
        data = []
        datasets = []
        identifiers = []

        for r in self.parts:
            r._graph = []
            rt = r.name[6:]
            if rt == 'specimen':
                specimens.append(r)
            if rt == 'process':
                processes.append(r)
            if rt == 'data':
                data.append(r)
            if rt == 'datasets':
                datasets.append(r)
            if rt == 'identifiers':
                identifiers.append(r)

        for specimen in specimens:
            self._graph.append(specimen)

        for process in processes:
            component_relationships = [x for x in process.relationships if x['@rel:type'] == 'IsPartOf']
            if self.name[6:] == 'specimen' or len(component_relationships) == 1:
                self._graph.append(process)
            else:
                for relationship in component_relationships:
                    for specimen in [x for x in self._graph if x.name[6:] == 'specimen']:
                        if relationship['@id'] == specimen.uuid:
                            specimen._graph.append(process)
                            break

        for dataset in datasets:
            self._graph.append(dataset)

        for d in data:
            component_relationships = [x for x in d.relationships if x['@rel:type'] == 'IsPartOf']
            if self.name[6:] == 'dataset' or len(component_relationships) == 1:
                self._graph.append(d)
            else:
                for relationship in component_relationships:
                    for dataset in [x for x in self._graph if x.name[6:] == 'dataset']:
                        if relationship['@id'] == dataset.uuid:
                            dataset._graph.append(d)
                            break

            process_relationships = [x for x in d.relationships if x['@rel:type'] == 'IsInputTo' or x['@rel:type'] == 'IsOutputOf']
            for relationship in process_relationships:
                match = False
                if self.name[6:] == 'process':
                    self._graph.append(d)
                    break

                for process in [x for x in self._graph if x.name[6:] == 'process']:
                    if relationship['@id'] == process.uuid:
                        process._graph.append(d)
                        match = True
                        break
                if not match:
                    for specimen in [x for x in self._graph if x.name[6:] == 'specimen']:
                        for process in [x for x in specimen._graph if x.name[6:] == 'process']:
                            if relationship['@id'] == process.uuid:
                                process._graph.append(d)
                                match = True
                                break
                        if match:
                            break

        for identifier in identifiers:
            component_relationships = [x for x in identifier.relationships if x['@rel:type'] == 'IsPartOf']
            if self.name[6:] == 'dataset' or len(component_relationships) == 1:
                self._graph.append(process)
            else:
                for relationship in component_relationships:
                        for dataset in [x for x in self._graph if x.name[6:] == 'dataset']:
                            if relationship['@id'] == dataset.uuid:
                                dataset._graph.append(identifier)
                                break
