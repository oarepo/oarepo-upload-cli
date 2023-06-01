from datetime import datetime
import json
import oracledb
from typing import Iterable

from cis_config import config
from .record import TestRecord
from oarepo_upload_cli.abstract_record_source import AbstractRecordSource


def dict_get(cursor):
    return [
        dict(zip([d[0] for d in cursor.description], r))
        for r in cursor.fetchall()
    ]


class TestSource(AbstractRecordSource):

    def __init__(self):
        self.db_connection = oracledb.connect(
            user=config.sis.user, password=config.sis.password,
            dsn=config.sis.dsn)
        # sanity check
        with self.db_connection.cursor() as cursor:
            cursor.execute("select 1 from dual")
            cursor.fetchall()

    def get_records(self, modified_after: datetime=None, modified_before: datetime=None) -> Iterable[TestRecord]:
        """
        Provides a generator that returns records within given timestamps.
        If no timestamps are given, returns all records.
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute("""
select * from (
select dipl.DID, max(nvl(fdt, ddt)) as m from dipl
left outer join dipl2doc on  dipl2doc.did=dipl.did
-- bakalarky, diplomky, disertacky
where DTYP in ('B', 'D', 'I')
-- soubor nebo metadata modifikovana po datumu
and greatest(ddt, nvl(fdt, ddt))>=:modified_after
group by dipl.did
-- seradit od nejmensiho datumu
) order by m
                    """, {"modified_after": modified_after})
            dids = {r[0]:r[1] for r in cursor.fetchall()}

            # TODO: merge in data from SZZ

            for did, modified in sorted(dids.items(), key=lambda x: (x[1], x[0])):
                # zakladni metadata
                cursor.execute("""

SELECT FAK.NAZEV                                           as zkratka_fakulty,
       fak.kod                                             as kod_fakulty,
       fak.text                                            as cesky_nazev_fakulty,
       fak.anazev                                          as anglicky_nazev_fakulty,
       STUD.SPRIJMENI                                      as prijmeni_studenta,
       STUD.SJMENO                                         as jmeno_studenta,
       STUD.STITUL                                         as titul_studenta,
       STUD.STITULZA                                       as titulza_studenta,
       stud.sdruh                                          as druh_studia,
       stud.soident                                        as oident_studenta,
       stud.sident                                         as id_studia,
       STUD.SSKR                                           as rok_studia,
       STUD.SOBOR                                          as zkratka_oboru,
       (select nazev from (select nazev from obor where kod = stud.sobor order by ddo desc) obor where rownum = 1)
                                                              cesky_nazev_oboru,
       (select anazev from (select anazev from obor where kod = stud.sobor order by ddo desc) obor where rownum = 1)
                                                              anglicky_nazev_oboru,
       STUD.SSTAV                                          as stav_studia,
-- --
       dzadost.dtyp                                        as utajeno_typ,
       dzadost.ddpodani                                    as utajeno_datum_podani,
       dzadost.dpevnalhuta                                 as utajeno_lhuta,
       dzadost.dzduvodneni                                 as utajeno_zduvodneni,
       dzadost.dpripominka                                 as utajeno_pripominka,
       dzadost.dstav                                       as utajeno_stav,
--
--
       dipl.did                                            as id_prace,
       dipl.dtyp                                           as typ_prace,
       ptyp.nazev                                          as cesky_typ_prace,
       ptyp.anazev                                         as anglicky_typ_prace,
       dipl.dnazev                                         as nazev_prace,
       dipl.danazev                                        as anglicky_nazev_prace,
       dipl.dcnazev                                        as cesky_nazev_prace,
       dipl.dskr                                           as rok_vypsani_prace,
       dipl.djazyk                                         as jazyk_prace,
       dnazev as nazev_prace,
       danazev as anglicky_nazev_prace,
       dcnazev as cesky_nazev_prace,
       CASE
           when dipl.dduspech IS not null then dipl.dduspech -- obcas neni nastaveny dduspech, tak se zkusi
           else
               (select max(datum_obhajoby_ze_zkousky)
                from (select case
                                 -- vzit posledni datum na zkousce, ktera odpovida
                                 -- predmetum diplomova, bakalarska ci disertacni prace
                                 when zkous.ZKDATUM3 IS not null then zkous.ZKDATUM3
                                 when zkous.ZKDATUM2 IS not null then zkous.ZKDATUM2
                                 when zkous.ZKDATUM1 IS not null then zkous.ZKDATUM1
                                 else null
                                 end as datum_obhajoby_ze_zkousky
                      from zkous
                      where zident = dident
                        and zpovinn IN ('S963008', 'S963011', 'N963008', 'N963010', 'S963010', 'N963014', 'N963007',
                                        'D965002', '963502', '963301')
                        AND (
                                  zvysl IN ('A', 'B', 'C', 'D', 'E', 'P')
                              OR zkvysl1 IN ('A', 'B', 'C', 'D', 'E', 'P')
                              OR zkvysl2 IN ('A', 'B', 'C', 'D', 'E', 'P')
                              OR zkvysl3 IN ('A', 'B', 'C', 'D', 'E', 'P')
                          )) datumy_zkousek)
           END                                             as datum_obhajoby,
       dipl.ddzadano                                       as datum_zadani,
       dipl.dustav                                         as kod_ustavu,
       dipl.dustav2                                        as kod_ustavu2,
       (select nazev from ustav where kod = dipl.dustav)   as cesky_nazev_ustavu,
       (select anazev from ustav where kod = dipl.dustav)  as anglicky_nazev_ustavu,
       (select nazev from ustav where kod = dipl.dustav2)  as cesky_nazev_ustavu2,
       (select anazev from ustav where kod = dipl.dustav2) as anglicky_nazev_ustavu2,
       dipl.duzavreno                                      as kod_uzavreni,
       dipl.ddt                                            as datum_posledni_zmeny
       -- dipl2doc.FAUTOR
--
from DIPL
     -- left outer join dipl2doc on dipl2doc.did = dipl.did
     left outer join FAK on fak.kod = dipl.DFAK
     left outer join STUD on SIDENT = dipl.DIDENT
     left outer join diplzadosti dzadost on dzadost.did = dipl.did
     left outer join ptyp on ptyp.kod = dipl.dtyp
where dipl.did=:did
                """, {'did': did})
                zakladni_metadata = dict_get(cursor)[0]

                cursor.execute("""
SELECT 
--
       u1.kod                                              as kod_vedouciho,
       u1.PRIJMENI                                         as prijmeni_vedouciho,
       u1.JMENO                                            as jmeno_vedouciho,
       u1.TITULPRED                                        as titul_vedouciho,
       u1.TITULZA                                          as titulza_vedouciho,
       u1.OIDENT                                           as oident_vedouciho,
--
       u2.kod                                              as kod_skolitele_specialisty,
       u2.PRIJMENI                                         as prijmeni_skolitele_specialisty,
       u2.JMENO                                            as jmeno_skolitele_specialisty,
       u2.TITULPRED                                        as titul_skolitele_specialisty,
       u2.TITULZA                                          as titulza_skolitele_specialisty,
       u2.oident                                           as oident_skolitele_specialisty,
--
       u3.kod                                              as kod_oponenta,
       u3.PRIJMENI                                         as prijmeni_oponenta,
       u3.JMENO                                            as jmeno_oponenta,
       u3.TITULPRED                                        as titul_oponenta,
       u3.TITULZA                                          as titulza_oponenta,
       u3.oident                                           as oident_oponenta,

       u7.kod                                              as kod_oponenta2,
       u7.PRIJMENI                                         as prijmeni_oponenta2,
       u7.JMENO                                            as jmeno_oponenta2,
       u7.TITULPRED                                        as titul_oponenta2,
       u7.TITULZA                                          as titulza_oponenta2,
       u7.oident                                           as oident_oponenta2,
--
       u8.kod                                              as kod_oponenta3,
       u8.PRIJMENI                                         as prijmeni_oponenta3,
       u8.JMENO                                            as jmeno_oponenta3,
       u8.TITULPRED                                        as titul_oponenta3,
       u8.TITULZA                                          as titulza_oponenta3,
       u8.oident                                           as oident_oponenta3,
--
       u9.kod                                              as kod_oponenta4,
       u9.PRIJMENI                                         as prijmeni_oponenta4,
       u9.JMENO                                            as jmeno_oponenta4,
       u9.TITULPRED                                        as titul_oponenta4,
       u9.TITULZA                                          as titulza_oponenta4,
       u9.oident                                           as oident_oponenta4,
--
       u4.kod                                              as kod_konzultanta1,
       u4.PRIJMENI                                         as prijmeni_konzultanta1,
       u4.JMENO                                            as jmeno_konzultanta1,
       u4.TITULPRED                                        as titul_konzultanta1,
       u4.TITULZA                                          as titulza_konzultanta1,
       u4.oident                                           as oident_konzultanta1,
--
       u5.kod                                              as kod_konzultanta2,
       u5.PRIJMENI                                         as prijmeni_konzultanta2,
       u5.JMENO                                            as jmeno_konzultanta2,
       u5.TITULPRED                                        as titul_konzultanta2,
       u5.TITULZA                                          as titulza_konzultanta2,
       u5.oident                                           as oident_konzultanta2,
--
       u6.kod                                              as kod_konzultanta3,
       u6.PRIJMENI                                         as prijmeni_konzultanta3,
       u6.JMENO                                            as jmeno_konzultanta3,
       u6.TITULPRED                                        as titul_konzultanta3,
       u6.TITULZA                                          as titulza_konzultanta3,
       u6.oident                                           as oident_konzultanta3
from DIPL
     -- left outer join dipl2doc on dipl2doc.did = dipl.did
     left outer join STUD on SIDENT = dipl.DIDENT
     left outer join UCIT u1 on u1.kod = dipl.DVEDOUCI
     left outer join UCIT u2 on u2.kod = STUD.SUCIT2
     left outer join UCIT u3 on u3.kod = dipl.DOPONENT
     left outer join UCIT u4 on u4.kod = dipl.DKONZULT1
     left outer join UCIT u5 on u5.kod = dipl.DKONZULT2
     left outer join UCIT u6 on u6.kod = dipl.DKONZULT3
     left outer join UCIT u7 on u7.kod = dipl.DOPONENT2
     left outer join UCIT u8 on u8.kod = dipl.DOPONENT3
     left outer join UCIT u9 on u9.kod = dipl.DOPONENT4
where did=:did
                """, {'did': did})
                lide = dict_get(cursor)[0]
                cursor.execute("""select * from dipl2doc where did=:did""", {
                    'did': did
                })
                soubory = dict_get(cursor)

                cursor.execute("""select * from DIPL_ANOTACE where did=:did""", did=did)
                anotace = dict_get(cursor)

                if zakladni_metadata['UTAJENO_TYP']:
                    # TODO: handle in a better way
                    continue

                rec = TestRecord(modified, zakladni_metadata, lide, soubory, anotace)
                with open('/tmp/md.json', 'w') as f:
                    json.dump(rec.metadata.metadata, f, indent=4, ensure_ascii=False)
                yield rec

    def get_records_count(self, modified_after: datetime=None, modified_before: datetime=None) -> int:
        """
        Approximates the size of a collection of records being returned.
        Modified before is ignored here ...
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute("""
SELECT count(1) from dipl 
where
    dipl.DTYP in ('B', 'D', 'I') 
and (
        -- metadata modifikovana po datu
        ddt>=:modified_after
    or 
        -- nebo nektery ze souboru modifikovan po datu
        (select max(fdt) from dipl2doc where dipl2doc.did=dipl.did)
        >=
        :modified_after
    )
            """, {"modified_after": modified_after})
            return cursor.fetchone()[0]
