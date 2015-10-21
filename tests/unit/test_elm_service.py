

def test_get_instances():

    from kmad_web.services.elm import ElmService

    test_id = "TAU_HUMAN"
    elm = ElmService(url="http://elm.eu.org/instances.gff?q={}".format(test_id))
    print elm.get_instances(test_id)
