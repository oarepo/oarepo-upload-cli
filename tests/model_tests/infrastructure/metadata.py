from oarepo_upload_cli.abstract_metadata import AbstractMetadata

class TestMetadata(AbstractMetadata):
    def __init__(self, zakladni_metadata, lide, anotace):
        self._metadata = {
            'metadata': non_empty_dict(
                thesis=non_empty_dict(
                    dateDefended=isoformat(zakladni_metadata['DATUM_OBHAJOBY']),
                    defended=not not zakladni_metadata['DATUM_OBHAJOBY'],
                    # degreeGrantors=[{
                    #     'id': degree_grantors[zakladni_metadata['KOD_USTAVU']]
                    # }]
                ),
                collection=zakladni_metadata['ZKRATKA_FAKULTY'],
                title=zakladni_metadata['NAZEV_PRACE'],
                # additionalTitles=non_empty_multilang(
                #     'en', zakladni_metadata['ANGLICKY_NAZEV_PRACE'],
                #     'cs', zakladni_metadata['CESKY_NAZEV_PRACE'],
                # ),
                creators=[
                    non_empty_dict(
                        nameType='Personal',
                        fullName=make_honorific_name(zakladni_metadata['JMENO_STUDENTA'],
                                                     zakladni_metadata['PRIJMENI_STUDENTA'],
                                                     zakladni_metadata['TITUL_STUDENTA'],
                                                     zakladni_metadata['TITULZA_STUDENTA'])
                    )
                ],
                # contributors=[
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'advisor'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_VEDOUCIHO'],
                #                                      lide['PRIJMENI_VEDOUCIHO'],
                #                                      lide['TITUL_VEDOUCIHO'], lide['TITULZA_VEDOUCIHO']),
                #         _if='fullName'
                #     ),
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'advisor'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_SKOLITELE_SPECIALISTY'],
                #                                      lide['PRIJMENI_SKOLITELE_SPECIALISTY'],
                #                                      lide['TITUL_SKOLITELE_SPECIALISTY'],
                #                                      lide['TITULZA_SKOLITELE_SPECIALISTY']),
                #         _if='fullName'
                #     ),
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'referee'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_OPONENTA'],
                #                                      lide['PRIJMENI_OPONENTA'],
                #                                      lide['TITUL_OPONENTA'],
                #                                      lide['TITULZA_OPONENTA']),
                #         _if='fullName'
                #     ),
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'referee'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_OPONENTA2'],
                #                                      lide['PRIJMENI_OPONENTA2'],
                #                                      lide['TITUL_OPONENTA2'],
                #                                      lide['TITULZA_OPONENTA2']),
                #         _if='fullName'
                #     ),
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'referee'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_OPONENTA3'],
                #                                      lide['PRIJMENI_OPONENTA3'],
                #                                      lide['TITUL_OPONENTA3'],
                #                                      lide['TITULZA_OPONENTA3']),
                #         _if='fullName'
                #     ),
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'referee'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_OPONENTA4'],
                #                                      lide['PRIJMENI_OPONENTA4'],
                #                                      lide['TITUL_OPONENTA4'],
                #                                      lide['TITULZA_OPONENTA4']),
                #         _if='fullName'
                #     ),
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'consultant'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_KONZULTANTA1'],
                #                                      lide['PRIJMENI_KONZULTANTA1'],
                #                                      lide['TITUL_KONZULTANTA1'],
                #                                      lide['TITULZA_KONZULTANTA1']),
                #         _if='fullName'
                #     ),
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'consultant'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_KONZULTANTA2'],
                #                                      lide['PRIJMENI_KONZULTANTA2'],
                #                                      lide['TITUL_KONZULTANTA2'],
                #                                      lide['TITULZA_KONZULTANTA2']),
                #         _if='fullName'
                #     ),
                #     non_empty_dict(
                #         nameType='Personal',
                #         role={
                #             'id': 'consultant'
                #         },
                #         fullName=make_honorific_name(lide['JMENO_KONZULTANTA3'],
                #                                      lide['PRIJMENI_KONZULTANTA3'],
                #                                      lide['TITUL_KONZULTANTA3'],
                #                                      lide['TITULZA_KONZULTANTA3']),
                #         _if='fullName'
                #     ),
                # ],
                # resourceType={
                #     'id': {
                #         'B': 'bachelor',
                #         'D': 'master',
                #         'I': 'doctoral'
                #     }[zakladni_metadata['TYP_PRACE']]
                # },
                dateAvailable=isoformat(zakladni_metadata['DATUM_OBHAJOBY']),
                dateModified=isoformat(zakladni_metadata['DATUM_POSLEDNI_ZMENY']),
                # languages=[
                #     {
                #         'id': zakladni_metadata['JAZYK_PRACE'] or 'cs'
                #     }
                # ],
                abstract=[
                    {
                        'lang': sislang2iso(an['DAJAZYK']),
                        'value': an['DATEXT'].read()
                    } for an in anotace if an['DATYP'] == 'ANO'
                ],
                # accessibility - nastavit, pokud nejsou soubory
                # accessRights={
                #     'id': 'c_abf2'  # otevřený přístup	open access
                #     # TODO: pridat nasledujici
                #     # c_f1cf	odložené zpřístupnění	embargoed access
                #     # c_16ec 	omezený přístup	restricted access
                #     # c_14cb	pouze metadata	metadata only access
                # }
            ),
            'id': str(zakladni_metadata['ID_PRACE'])
        }

    @property
    def metadata(self):
        return self._metadata

    @property
    def modified(self):
        return self._metadata['metadata']['dateModified']

def non_empty_dict(**kwargs):
    if '_if' in kwargs:
        if not kwargs[kwargs['_if']]:
            return {}
    return {
        k: v for k, v in kwargs.items() if (v or v is False) and k != '_if'
    }

def make_honorific_name(jmeno, prijmeni, titul, titulza):
    ret = []
    if titul:
        ret.append(titul)
    if jmeno:
        if ret:
            ret.append(' ')
        ret.append(jmeno)
    if prijmeni:
        if ret:
            ret.append(' ')
        ret.append(prijmeni)
    if titulza:
        ret.append(', ')
        ret.append(titulza)
    return ''.join(ret)


def isoformat(x):
    if x:
        return x.date().strftime('%Y-%m-%d')
    return x

def sislang2iso(x):
    return {
        'RUS': 'ru',
        'ENG': 'en',
        'FRE': 'fr',
        'CZE': 'cs',
        'CSE': 'cs',
        'SLO': 'sk',
        'SLV': 'sl'
    }.get(x, None)