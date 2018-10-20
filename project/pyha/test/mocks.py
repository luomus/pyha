#coding=utf-8
#json-muotoinen pyyntö
JSON_MOCK = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B16BD",
	"source": "KE.398",
	"email": "ex.apmle@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"linnut",
				"nisäkkäät"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "HR.39",
			"conservationReasonCount": 1031,
			"customReasonCount": 1031
		},
		{
			"id": "HR.447",
			"conservationReasonCount": 904,
			"customReasonCount": 904
		},
		{
			"id": "HR.60",
			"conservationReasonCount": 14,
			"customReasonCount": 14
		}
	]
}'''

#eroaa ensimmäisestä id:n osalta
JSON_MOCK2 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B16BE",
	"source": "KE.398",
	"email": "ex@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"linnut",
				"salaporsaat"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "HR.39",
			"conservationReasonCount": 1031,
			"customReasonCount": 1031
		},
		{
			"id": "HR.447",
			"conservationReasonCount": 904,
			"customReasonCount": 904
		},
		{
			"id": "HR.60",
			"conservationReasonCount": 14,
			"customReasonCount": 14
		}
	]
}'''

#jsonista puuttuu filtterit
JSON_MOCK3 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B15555",
	"source": "KE.398",
	"email": "filters@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"collections": [
		{
			"id": "HR.39",
			"conservationReasonCount": 1031,
			"customReasonCount": 1031
		},
		{
			"id": "HR.447",
			"conservationReasonCount": 904,
			"customReasonCount": 904
		},
		{
			"id": "HR.60",
			"conservationReasonCount": 14,
			"customReasonCount": 14
		}
	]
}'''

#mock4 on email-testausta varten
JSON_MOCK4 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B12LL",
	"description": "Testausta",
	"source": "KE.398",
	"email": "te.staaja@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"testilinnut",
				"testinisäkkäät"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "HR.48",
			"conservationReasonCount": 1031,
			"customReasonCount": 1031
		},
		{
			"id": "HR.447",
			"conservationReasonCount": 904,
			"customReasonCount": 904
		},
		{
			"id": "HR.60",
			"conservationReasonCount": 14,
			"customReasonCount": 14
		}
	]
}'''
#sama pyyntö kuin mock4, mutta eri id ja kuvaus
JSON_MOCK5 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B12LÖ",
	"description": "Testausta2",
	"source": "KE.398",
	"email": "te.staaja@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"testilinnut",
				"testinisäkkäät"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "HR.39",
			"conservationReasonCount": 1031,
			"customReasonCount": 1031
		},
		{
			"id": "HR.447",
			"conservationReasonCount": 904,
			"customReasonCount": 904
		},
		{
			"id": "HR.60",
			"conservationReasonCount": 14,
			"customReasonCount": 14
		}
	]
}'''
#mock6:sta löytyy secure reasonien määriä
JSON_MOCK6 = '''	
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775sdB16BD",
	"source": "KE.398",
	"email": "test123@321.asdfgh",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"linnut",
				"nisäkkäät"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "colcustomsec1",
			"customReasonCount": 1
		},
		{
			"id": "colsecured",
			"conservationReasonCount": 3,
			"customReasonCount": 2
		}
	]
	}
  '''
  #jsonmock7:sta löytyy oikeat filtterit ja metadata-alkuinenkin filtteri
JSON_MOCK7= '''
  {
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B16AB",
	"source": "KE.398",
	"email": "pyhatestaaja@gmail.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"informalTaxonGroupId": [
				"MVL.140",
				"MVL.185"
			]
		},
		{
			"administrativeStatusId": [
				"MX.finlex160_1997_appendix4"
			]
		},
		{
			"time": [
				"2000/"
			]
		},
		{
			"secured": [
				"true"
			]
		}
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			],
			"mainSecureReasons": {
        "DEFAULT_TAXON_CONSERVATION": {
          "count": 3
        },
        "CUSTOM": {
          "count": 2
        }
      }
		},
		{
			"id": "HR.39",
			"conservationReasonCount": 3,
			"customReasonCount": 2
		},
		{
			"id": "HR.447",
			"customReasonCount": 1
		},
		{
			"id": "HR.447"
		}
	]
	}
  '''
