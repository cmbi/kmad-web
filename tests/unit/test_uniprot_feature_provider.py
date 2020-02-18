from nose.tools import eq_, ok_, with_setup

from kmad_web.services.helpers.cache import cache_manager as cm
from kmad_web.domain.features.providers.uniprot import UniprotFeatureProvider


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@with_setup(setup, teardown)
def test_get_ptms():
    uniprot = UniprotFeatureProvider()
    result = uniprot.get_ptms('TAU_HUMAN')
    ok_(result)

    result = uniprot.get_ptms('P21815')
    expected = [{
        "info": "Phosphoserine",
        "position": 31,
        "annotation_level": 0,
        "name": "phosphorylation"
    },
    {
        "info": "Phosphoserine",
        "position": 67,
        "annotation_level": 1,
        "name": "phosphorylation"
    },
    {
        "info": "Phosphoserine",
        "position": 74,
        "annotation_level": 1,
        "name": "phosphorylation"
    },
    {
        "info": "Phosphoserine",
        "position": 75,
        "annotation_level": 1,
        "name": "phosphorylation"
    },
    {
        "info": "Phosphoserine",
        "position": 94,
        "annotation_level": 1,
        "name": "phosphorylation"
    },
    {
        "info": "Phosphoserine",
        "position": 100,
        "annotation_level": 1,
        "name": "phosphorylation"
    },
    {
        "info": "Phosphoserine",
        "position": 149,
        "annotation_level": 1,
        "name": "phosphorylation"
    },
    {
        "info": "Phosphoserine",
        "position": 280,
        "annotation_level": 1,
        "name": "phosphorylation"
    },
    {
        "info": "Sulfotyrosine",
        "position": 313,
        "annotation_level": 0,
        "name": "Sulfotyrosine"
    },
    {
        "info": "Sulfotyrosine",
        "position": 314,
        "annotation_level": 0,
        "name": "Sulfotyrosine"
    },
    {
        "info": "N-linked (GlcNAc...) asparagine",
        "position": 104,
        "annotation_level": 1,
        "name": "N-glycosylation"
    },
    {
        "info": "O-linked (GalNAc...) threonine",
        "position": 119,
        "annotation_level": 2,
        "name": "O-glycosylation"
    },
    {
        "info": "O-linked (GalNAc...) threonine",
        "position": 122,
        "annotation_level": 2,
        "name": "O-glycosylation"
    },
    {
        "info": "N-linked (GlcNAc...) asparagine",
        "position": 177,
        "annotation_level": 1,
        "name": "N-glycosylation"
    },
    {
        "info": "N-linked (GlcNAc...) asparagine",
        "position": 182,
        "annotation_level": 1,
        "name": "N-glycosylation"
    },
    {
        "info": "N-linked (GlcNAc...) asparagine",
        "position": 190,
        "annotation_level": 1,
        "name": "N-glycosylation"
    },
    {
        "info": "O-linked (GalNAc...) threonine",
        "position": 227,
        "annotation_level": 2,
        "name": "O-glycosylation"
    },
    {
        "info": "O-linked (GalNAc...) threonine",
        "position": 228,
        "annotation_level": 2,
        "name": "O-glycosylation"
    },
    {
        "info": "O-linked (GalNAc...) threonine",
        "position": 229,
        "annotation_level": 2,
        "name": "O-glycosylation"
    },
    {
        "info": "O-linked (GalNAc...) threonine",
        "position": 238,
        "annotation_level": 2,
        "name": "O-glycosylation"
    },
    {
        "info": "O-linked (GalNAc...) threonine",
        "position": 239,
        "annotation_level": 2,
        "name": "O-glycosylation"
    }]
    eq_(result, expected)


def test_get_ptm_type():
    ptm_name = "Phosphoserine; by PDPK1 and TTBK1."
    expected_type = 'phosphorylation'
    uniprot = UniprotFeatureProvider()
    eq_(expected_type, uniprot._get_ptm_type(ptm_name))
