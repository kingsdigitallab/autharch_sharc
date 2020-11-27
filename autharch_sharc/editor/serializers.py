from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .documents import EADDocument


class EADDocumentResultSerializer(DocumentSerializer):
    """ Serializer for EAD XML document"""

    class Meta:
        document = EADDocument

        fields = (
            'pk',
            'reference',
            'unittitle',
            'category',
            'size',
            "medium",
            "label",
            'creators',
            'date_of_creation',
            # creation_date_notes: "creation_date_note",
            'place_of_origin',
            'date_of_acquisition',
            # acquisition_dates_notes
            #  provenance: "provenance",
            # 'connection_primary',
            # 'connection_secondary',
            # 'connection_type',
            # 'publicationstatus_value',
            'related_material',
            'related_sources',
            'related_people',
            'media'
        )

        """

                related_sources: {
                    individual_connections: ["individual_connection1",
                    "individual_connection2"],
                    works: ["work1", "work2"],
                    texts: ["text1", "text2"],
                    performances: ["performance1", "performance2"],
                    sources: ["source1", "source2"],
                },
                related_people: {
                    acquirers: ["acquirer1", "acquirer2"],
                    publishers: ["publisher1", "publisher2"],
                    donors: ["donor1", "donor2"]
                },
                related_entries: [
                    {
                        id: 0,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/34658/full
                        /thm/0/default.jpg",
                        type: 'Painting',
                        title: "A Scene from Macbeth, Act I"
                    },
                    {
                        id: 1,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/32427/full
                        /thm/0/default.jpg",
                        type: 'Print',
                        title: "Giorgio Frederico Augusto Principe di Galles"
                    },
                    {
                        id: 2,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/34658/full
                        /thm/0/default.jpg",
                        type: 'Painting',
                        title: "A performance of Macbeth in the Rubens Room,
                        Windsor Catle, 4 February 1853"
                    },
                    {
                        id: 0,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/37/full
                        /thm/0/default.jpg",
                        type: 'Painting',
                        title: "A Scene from Macbeth, Act I"
                    },
                    {
                        id: 1,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/34658/full
                        /thm/0/default.jpg",
                        type: 'Print',
                        title: "Giorgio Frederico Augusto Principe di Galles"
                    },
                    {
                        id: 2,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/37/full
                        /thm/0/default.jpg",
                        type: 'Painting',
                        title: "A performance of Macbeth in the Rubens Room,
                        Windsor Catle, 4 February 1853"
                    }
                ],
                notes: "Notes",
                label: "label/inscription/caption",
                publication_details: "publication_details",
                published_references: ["published_reference1",
                "published_reference2"],
                // TODO: change to an array of unpublished records once the
                data is normalised
                unpublished_references: "unpublished_references",
                media: [
                    // this will need to change based on the data that is
                    sent from the backend
                    // I don't know what data is currently being sent - I
                    have checked a few objects and all I see is media: [],
                    // but on line 117 below someone has already added a
                    function to get the right data, so there must be
                    something already set up for media
                    {
                        id: 0,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/34658/full
                        /thm/0/default.jpg",
                        title: "image 1"
                    },
                    {
                        id: 1,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/32427/full
                        /thm/0/default.jpg",
                        title: "image 2"
                    },
                    {
                        id: 2,
                        resource:
                        "https://rct.resourcespace.com/iiif/image/37/full
                        /thm/0/default.jpg",
                        title: "image 3"
                    },
                ],

        """
