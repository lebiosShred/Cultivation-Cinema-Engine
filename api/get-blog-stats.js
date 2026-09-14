const crypto = require('crypto');

const AUTH_SECRET = process.env.DASHBOARD_AUTH_SECRET || 'octane_secure_hmac_secret_2026_x89a';

const BLOG_DATASETS = {
  "90d": {
    "clicks": 923,
    "impressions": 311775,
    "blogCount": 270,
    "topBlogs": [
      {
        "url": "https://blog.octanesolutions.com.au/a-tm1-guide-on-how-to-for-dummies",
        "title": "a TM1 Guide on How to for Dummies",
        "clicks": 42,
        "impressions": 32591,
        "ctr": 0.0012886993341720107,
        "position": 8.307446841152466,
        "prevClicks": 86,
        "prevImpressions": 31282,
        "clicksChange": -51.162790697674424,
        "impressionsChange": 4.184515056582059
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-project-bob-the-beginning-of-enterprise-grade-agentic-software-development",
        "title": "IBM Project Bob the Beginning of Enterprise Grade Agentic Software Development",
        "clicks": 42,
        "impressions": 24530,
        "ctr": 0.0017121891561353445,
        "position": 8.400529963310232,
        "prevClicks": 77,
        "prevImpressions": 33025,
        "clicksChange": -45.45454545454545,
        "impressionsChange": -25.722937168811505
      },
      {
        "url": "https://blog.octanesolutions.com.au/cognos-analytics-11.0.11.0-is-now-available-for-download",
        "title": "Cognos Analytics 11.0.11.0 is Now Available for Download",
        "clicks": 41,
        "impressions": 2777,
        "ctr": 0.014764133957508103,
        "position": 7.734965790421318,
        "prevClicks": 39,
        "prevImpressions": 4459,
        "clicksChange": 5.128205128205128,
        "impressionsChange": -37.72146221125813
      },
      {
        "url": "https://blog.octanesolutions.com.au/the-ultimate-ibm-planning-analytics-tm1-training-roadmap-for-beginners",
        "title": "the Ultimate IBM Planning Analytics TM1 Training Roadmap for Beginners",
        "clicks": 39,
        "impressions": 5576,
        "ctr": 0.006994261119081779,
        "position": 11.612804878048781,
        "prevClicks": 3,
        "prevImpressions": 1277,
        "clicksChange": 1200,
        "impressionsChange": 336.6483946750196
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-planning-analytics-for-excel-bug-and-its-fix",
        "title": "IBM Planning Analytics for Excel Bug and Its Fix",
        "clicks": 37,
        "impressions": 4175,
        "ctr": 0.008862275449101797,
        "position": 10.301556886227544,
        "prevClicks": 71,
        "prevImpressions": 7226,
        "clicksChange": -47.88732394366197,
        "impressionsChange": -42.22252975366732
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-watsonx-orchestrate-use-cases",
        "title": "IBM Watsonx Orchestrate Use Cases",
        "clicks": 35,
        "impressions": 8993,
        "ctr": 0.0038919159346158124,
        "position": 8.437562548648948,
        "prevClicks": 38,
        "prevImpressions": 22940,
        "clicksChange": -7.894736842105263,
        "impressionsChange": -60.79773321708806
      },
      {
        "url": "https://blog.octanesolutions.com.au/whats-new-in-cognos-analytics-12.1.x",
        "title": "Whats New in Cognos Analytics 12.1.x",
        "clicks": 34,
        "impressions": 4114,
        "ctr": 0.008264462809917356,
        "position": 9.13563441905688,
        "prevClicks": 78,
        "prevImpressions": 11072,
        "clicksChange": -56.41025641025641,
        "impressionsChange": -62.84320809248555
      },
      {
        "url": "https://blog.octanesolutions.com.au/unlocking-the-power-of-ibm-planning-analytics-with-execute-http-request",
        "title": "Unlocking the Power of IBM Planning Analytics With Execute Http Request",
        "clicks": 26,
        "impressions": 3240,
        "ctr": 0.008024691358024692,
        "position": 10.526234567901234,
        "prevClicks": 34,
        "prevImpressions": 5839,
        "clicksChange": -23.52941176470588,
        "impressionsChange": -44.51104641205686
      },
      {
        "url": "https://blog.octanesolutions.com.au/dynamizing-dynamic-reports-hacks",
        "title": "Dynamizing Dynamic Reports Hacks",
        "clicks": 18,
        "impressions": 1475,
        "ctr": 0.012203389830508475,
        "position": 11.622372881355933,
        "prevClicks": 20,
        "prevImpressions": 3992,
        "clicksChange": -10,
        "impressionsChange": -63.051102204408814
      },
      {
        "url": "https://blog.octanesolutions.com.au/worried-about-data-spreading-in-consolidations-here-is-how",
        "title": "Worried About Data Spreading in Consolidations Here is How",
        "clicks": 18,
        "impressions": 641,
        "ctr": 0.028081123244929798,
        "position": 8.677067082683308,
        "prevClicks": 17,
        "prevImpressions": 607,
        "clicksChange": 5.88235294117647,
        "impressionsChange": 5.601317957166392
      },
      {
        "url": "https://blog.octanesolutions.com.au/take-complexity-out-of-excel-and-systemize-your-data-with-ibm-cognos-tm1-and-planning-analytics",
        "title": "Take Complexity Out of Excel and Systemize Your Data With IBM Cognos TM1 and Planning Analytics",
        "clicks": 17,
        "impressions": 5639,
        "ctr": 0.0030147189217946445,
        "position": 14.585564816456818,
        "prevClicks": 7,
        "prevImpressions": 5255,
        "clicksChange": 142.85714285714286,
        "impressionsChange": 7.30732635585157
      },
      {
        "url": "https://blog.octanesolutions.com.au/unveiling-dynamic-lists",
        "title": "Unveiling Dynamic Lists",
        "clicks": 17,
        "impressions": 1735,
        "ctr": 0.009798270893371758,
        "position": 9.740634005763688,
        "prevClicks": 31,
        "prevImpressions": 3221,
        "clicksChange": -45.16129032258064,
        "impressionsChange": -46.134740763737966
      },
      {
        "url": "https://blog.octanesolutions.com.au/agentic-ai-in-finance-tm1-why-everyones-suddenly-talking-about-it",
        "title": "Agentic AI in Finance TM1 Why Everyones Suddenly Talking About It",
        "clicks": 16,
        "impressions": 3972,
        "ctr": 0.004028197381671702,
        "position": 15.446122860020141,
        "prevClicks": 30,
        "prevImpressions": 11445,
        "clicksChange": -46.666666666666664,
        "impressionsChange": -65.29488859764089
      },
      {
        "url": "https://blog.octanesolutions.com.au/tm1-undocumented-function-renaming-the-element-name",
        "title": "TM1 Undocumented Function Renaming the Element Name",
        "clicks": 16,
        "impressions": 1033,
        "ctr": 0.015488867376573089,
        "position": 8.747337850919651,
        "prevClicks": 15,
        "prevImpressions": 969,
        "clicksChange": 6.666666666666667,
        "impressionsChange": 6.604747162022703
      },
      {
        "url": "https://blog.octanesolutions.com.au/dashboard/session-timeout-for-tm1web-paw-and-pax",
        "title": "Dashboard/session Timeout for Tm1web PAW and PAX",
        "clicks": 15,
        "impressions": 956,
        "ctr": 0.015690376569037656,
        "position": 8.061715481171548,
        "prevClicks": 25,
        "prevImpressions": 1332,
        "clicksChange": -40,
        "impressionsChange": -28.22822822822823
      },
      {
        "url": "https://blog.octanesolutions.com.au/enabling-and-configuring-alerts-for-ibm-planning-analytics-application-and-server",
        "title": "Enabling and Configuring Alerts for IBM Planning Analytics Application and Server",
        "clicks": 14,
        "impressions": 1133,
        "ctr": 0.01235657546337158,
        "position": 8.911738746690203,
        "prevClicks": 26,
        "prevImpressions": 2415,
        "clicksChange": -46.15384615384615,
        "impressionsChange": -53.084886128364396
      },
      {
        "url": "https://blog.octanesolutions.com.au/smarter-cube-views-in-ibm-planning-analytics-workspace-3.1.3",
        "title": "Smarter Cube Views in IBM Planning Analytics Workspace 3.1.3",
        "clicks": 13,
        "impressions": 1637,
        "ctr": 0.00794135613927917,
        "position": 8.9529627367135,
        "prevClicks": 15,
        "prevImpressions": 2421,
        "clicksChange": -13.333333333333334,
        "impressionsChange": -32.38331268071045
      },
      {
        "url": "https://blog.octanesolutions.com.au/best-practices-for-maximumports-in-tm1-avoiding-paw-connection-failures",
        "title": "Best Practices for Maximumports in TM1 Avoiding PAW Connection Failures",
        "clicks": 13,
        "impressions": 879,
        "ctr": 0.01478953356086462,
        "position": 8.41296928327645,
        "prevClicks": 9,
        "prevImpressions": 943,
        "clicksChange": 44.44444444444444,
        "impressionsChange": -6.786850477200425
      },
      {
        "url": "https://blog.octanesolutions.com.au/tips-on-how-to-manage-your-tm1-effectively",
        "title": "Tips on How to Manage Your TM1 Effectively",
        "clicks": 12,
        "impressions": 1273,
        "ctr": 0.009426551453260016,
        "position": 16.70384917517675,
        "prevClicks": 16,
        "prevImpressions": 6177,
        "clicksChange": -25,
        "impressionsChange": -79.39129027035779
      },
      {
        "url": "https://blog.octanesolutions.com.au/visual-analysis-crafting-compelling-dashboards-in-ibm-planning-analytics-workspace",
        "title": "Visual Analysis Crafting Compelling Dashboards in IBM Planning Analytics Workspace",
        "clicks": 12,
        "impressions": 356,
        "ctr": 0.033707865168539325,
        "position": 7.404494382022472,
        "prevClicks": 11,
        "prevImpressions": 1183,
        "clicksChange": 9.090909090909092,
        "impressionsChange": -69.90701606086222
      }
    ]
  },
  "30d": {
    "clicks": 273,
    "impressions": 94127,
    "blogCount": 254,
    "topBlogs": [
      {
        "url": "https://blog.octanesolutions.com.au/the-ultimate-ibm-planning-analytics-tm1-training-roadmap-for-beginners",
        "title": "the Ultimate IBM Planning Analytics TM1 Training Roadmap for Beginners",
        "clicks": 16,
        "impressions": 1732,
        "ctr": 0.009237875288683603,
        "position": 13.083140877598153,
        "prevClicks": 13,
        "prevImpressions": 2174,
        "clicksChange": 23.076923076923077,
        "impressionsChange": -20.3311867525299
      },
      {
        "url": "https://blog.octanesolutions.com.au/a-tm1-guide-on-how-to-for-dummies",
        "title": "a TM1 Guide on How to for Dummies",
        "clicks": 15,
        "impressions": 12847,
        "ctr": 0.0011675877636802365,
        "position": 6.81038374717833,
        "prevClicks": 13,
        "prevImpressions": 8814,
        "clicksChange": 15.384615384615385,
        "impressionsChange": 45.75675062400726
      },
      {
        "url": "https://blog.octanesolutions.com.au/cognos-analytics-11.0.11.0-is-now-available-for-download",
        "title": "Cognos Analytics 11.0.11.0 is Now Available for Download",
        "clicks": 14,
        "impressions": 646,
        "ctr": 0.021671826625386997,
        "position": 8.797213622291022,
        "prevClicks": 17,
        "prevImpressions": 754,
        "clicksChange": -17.647058823529413,
        "impressionsChange": -14.323607427055704
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-watsonx-orchestrate-use-cases",
        "title": "IBM Watsonx Orchestrate Use Cases",
        "clicks": 12,
        "impressions": 3383,
        "ctr": 0.0035471475022169673,
        "position": 8.065622228791014,
        "prevClicks": 8,
        "prevImpressions": 1763,
        "clicksChange": 50,
        "impressionsChange": 91.88882586500283
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-planning-analytics-for-excel-bug-and-its-fix",
        "title": "IBM Planning Analytics for Excel Bug and Its Fix",
        "clicks": 10,
        "impressions": 1356,
        "ctr": 0.007374631268436578,
        "position": 11.914454277286136,
        "prevClicks": 12,
        "prevImpressions": 1136,
        "clicksChange": -16.666666666666664,
        "impressionsChange": 19.366197183098592
      },
      {
        "url": "https://blog.octanesolutions.com.au/mastering-mdx-in-ibm-planning-analytics-workspace",
        "title": "Mastering Mdx in IBM Planning Analytics Workspace",
        "clicks": 10,
        "impressions": 691,
        "ctr": 0.01447178002894356,
        "position": 10.945007235890014,
        "prevClicks": 1,
        "prevImpressions": 307,
        "clicksChange": 900,
        "impressionsChange": 125.08143322475568
      },
      {
        "url": "https://blog.octanesolutions.com.au/whats-new-in-cognos-analytics-12.1.x",
        "title": "Whats New in Cognos Analytics 12.1.x",
        "clicks": 9,
        "impressions": 1152,
        "ctr": 0.0078125,
        "position": 10.638020833333334,
        "prevClicks": 13,
        "prevImpressions": 1128,
        "clicksChange": -30.76923076923077,
        "impressionsChange": 2.127659574468085
      },
      {
        "url": "https://blog.octanesolutions.com.au/worried-about-data-spreading-in-consolidations-here-is-how",
        "title": "Worried About Data Spreading in Consolidations Here is How",
        "clicks": 8,
        "impressions": 178,
        "ctr": 0.0449438202247191,
        "position": 8.820224719101123,
        "prevClicks": 4,
        "prevImpressions": 203,
        "clicksChange": 100,
        "impressionsChange": -12.31527093596059
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-project-bob-the-beginning-of-enterprise-grade-agentic-software-development",
        "title": "IBM Project Bob the Beginning of Enterprise Grade Agentic Software Development",
        "clicks": 7,
        "impressions": 5081,
        "ctr": 0.0013776815587482779,
        "position": 9.597126549891753,
        "prevClicks": 14,
        "prevImpressions": 6039,
        "clicksChange": -50,
        "impressionsChange": -15.8635535684716
      },
      {
        "url": "https://blog.octanesolutions.com.au/chatgpt-for-enterprise-reimagine",
        "title": "Chatgpt for Enterprise Reimagine",
        "clicks": 7,
        "impressions": 2299,
        "ctr": 0.003044802087864289,
        "position": 12.375380600260984,
        "prevClicks": 0,
        "prevImpressions": 730,
        "clicksChange": 100,
        "impressionsChange": 214.93150684931507
      },
      {
        "url": "https://blog.octanesolutions.com.au/take-complexity-out-of-excel-and-systemize-your-data-with-ibm-cognos-tm1-and-planning-analytics",
        "title": "Take Complexity Out of Excel and Systemize Your Data With IBM Cognos TM1 and Planning Analytics",
        "clicks": 7,
        "impressions": 2143,
        "ctr": 0.0032664489034064394,
        "position": 13.932337844143724,
        "prevClicks": 2,
        "prevImpressions": 1121,
        "clicksChange": 250,
        "impressionsChange": 91.1685994647636
      },
      {
        "url": "https://blog.octanesolutions.com.au/unlocking-the-power-of-ibm-planning-analytics-with-execute-http-request",
        "title": "Unlocking the Power of IBM Planning Analytics With Execute Http Request",
        "clicks": 7,
        "impressions": 625,
        "ctr": 0.0112,
        "position": 12.6672,
        "prevClicks": 6,
        "prevImpressions": 796,
        "clicksChange": 16.666666666666664,
        "impressionsChange": -21.482412060301506
      },
      {
        "url": "https://blog.octanesolutions.com.au/best-practices-for-maximumports-in-tm1-avoiding-paw-connection-failures",
        "title": "Best Practices for Maximumports in TM1 Avoiding PAW Connection Failures",
        "clicks": 7,
        "impressions": 278,
        "ctr": 0.025179856115107913,
        "position": 9.93525179856115,
        "prevClicks": 2,
        "prevImpressions": 253,
        "clicksChange": 250,
        "impressionsChange": 9.881422924901186
      },
      {
        "url": "https://blog.octanesolutions.com.au/dynamizing-dynamic-reports-hacks",
        "title": "Dynamizing Dynamic Reports Hacks",
        "clicks": 5,
        "impressions": 445,
        "ctr": 0.011235955056179775,
        "position": 15.26067415730337,
        "prevClicks": 7,
        "prevImpressions": 488,
        "clicksChange": -28.57142857142857,
        "impressionsChange": -8.811475409836065
      },
      {
        "url": "https://blog.octanesolutions.com.au/drill-down-using-slicer-in-power-bi",
        "title": "Drill Down Using Slicer in Power BI",
        "clicks": 5,
        "impressions": 376,
        "ctr": 0.013297872340425532,
        "position": 11.63563829787234,
        "prevClicks": 3,
        "prevImpressions": 312,
        "clicksChange": 66.66666666666666,
        "impressionsChange": 20.51282051282051
      },
      {
        "url": "https://blog.octanesolutions.com.au/build-better-ai-agents-with-ibm-watson-orchestrate-adk",
        "title": "Build Better AI Agents With IBM Watson Orchestrate Adk",
        "clicks": 4,
        "impressions": 1375,
        "ctr": 0.002909090909090909,
        "position": 10.821090909090909,
        "prevClicks": 4,
        "prevImpressions": 1684,
        "clicksChange": 0,
        "impressionsChange": -18.34916864608076
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-planning-analytics-tm1-anaplan-an-ernest-comparison",
        "title": "IBM Planning Analytics TM1 Anaplan An Ernest Comparison",
        "clicks": 4,
        "impressions": 466,
        "ctr": 0.008583690987124463,
        "position": 17.871244635193133,
        "prevClicks": 0,
        "prevImpressions": 393,
        "clicksChange": 100,
        "impressionsChange": 18.575063613231553
      },
      {
        "url": "https://blog.octanesolutions.com.au/planning-analytics-workspace-local-distributed",
        "title": "Planning Analytics Workspace Local Distributed",
        "clicks": 4,
        "impressions": 378,
        "ctr": 0.010582010582010581,
        "position": 20.17989417989418,
        "prevClicks": 2,
        "prevImpressions": 336,
        "clicksChange": 100,
        "impressionsChange": 12.5
      },
      {
        "url": "https://blog.octanesolutions.com.au/tips-on-how-to-manage-your-tm1-effectively",
        "title": "Tips on How to Manage Your TM1 Effectively",
        "clicks": 4,
        "impressions": 302,
        "ctr": 0.013245033112582781,
        "position": 19.956953642384107,
        "prevClicks": 1,
        "prevImpressions": 329,
        "clicksChange": 300,
        "impressionsChange": -8.206686930091186
      },
      {
        "url": "https://blog.octanesolutions.com.au/using-rules-and-feeders",
        "title": "Using Rules and Feeders",
        "clicks": 4,
        "impressions": 119,
        "ctr": 0.03361344537815126,
        "position": 17.680672268907564,
        "prevClicks": 1,
        "prevImpressions": 174,
        "clicksChange": 300,
        "impressionsChange": -31.60919540229885
      }
    ]
  },
  "7d": {
    "clicks": 62,
    "impressions": 23832,
    "blogCount": 231,
    "topBlogs": [
      {
        "url": "https://blog.octanesolutions.com.au/chatgpt-for-enterprise-reimagine",
        "title": "Chatgpt for Enterprise Reimagine",
        "clicks": 4,
        "impressions": 668,
        "ctr": 0.005988023952095809,
        "position": 8.905688622754491,
        "prevClicks": 2,
        "prevImpressions": 472,
        "clicksChange": 100,
        "impressionsChange": 41.52542372881356
      },
      {
        "url": "https://blog.octanesolutions.com.au/the-ultimate-ibm-planning-analytics-tm1-training-roadmap-for-beginners",
        "title": "the Ultimate IBM Planning Analytics TM1 Training Roadmap for Beginners",
        "clicks": 4,
        "impressions": 290,
        "ctr": 0.013793103448275862,
        "position": 15.089655172413794,
        "prevClicks": 3,
        "prevImpressions": 320,
        "clicksChange": 33.33333333333333,
        "impressionsChange": -9.375
      },
      {
        "url": "https://blog.octanesolutions.com.au/cognos-analytics-11.0.11.0-is-now-available-for-download",
        "title": "Cognos Analytics 11.0.11.0 is Now Available for Download",
        "clicks": 4,
        "impressions": 158,
        "ctr": 0.02531645569620253,
        "position": 9.468354430379748,
        "prevClicks": 3,
        "prevImpressions": 130,
        "clicksChange": 33.33333333333333,
        "impressionsChange": 21.53846153846154
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-planning-analytics-tm1-anaplan-an-ernest-comparison",
        "title": "IBM Planning Analytics TM1 Anaplan An Ernest Comparison",
        "clicks": 3,
        "impressions": 100,
        "ctr": 0.03,
        "position": 23.69,
        "prevClicks": 1,
        "prevImpressions": 93,
        "clicksChange": 200,
        "impressionsChange": 7.526881720430108
      },
      {
        "url": "https://blog.octanesolutions.com.au/mastering-mdx-in-ibm-planning-analytics-workspace",
        "title": "Mastering Mdx in IBM Planning Analytics Workspace",
        "clicks": 3,
        "impressions": 99,
        "ctr": 0.030303030303030304,
        "position": 15.575757575757576,
        "prevClicks": 0,
        "prevImpressions": 281,
        "clicksChange": 100,
        "impressionsChange": -64.76868327402136
      },
      {
        "url": "https://blog.octanesolutions.com.au/a-tm1-guide-on-how-to-for-dummies",
        "title": "a TM1 Guide on How to for Dummies",
        "clicks": 2,
        "impressions": 3642,
        "ctr": 0.0005491488193300384,
        "position": 6.607907742998353,
        "prevClicks": 5,
        "prevImpressions": 3179,
        "clicksChange": -60,
        "impressionsChange": 14.564328405158856
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-watsonx-orchestrate-use-cases",
        "title": "IBM Watsonx Orchestrate Use Cases",
        "clicks": 2,
        "impressions": 623,
        "ctr": 0.0032102728731942215,
        "position": 7.645264847512038,
        "prevClicks": 8,
        "prevImpressions": 629,
        "clicksChange": -75,
        "impressionsChange": -0.9538950715421303
      },
      {
        "url": "https://blog.octanesolutions.com.au/whats-new-in-cognos-analytics-12.1.x",
        "title": "Whats New in Cognos Analytics 12.1.x",
        "clicks": 2,
        "impressions": 245,
        "ctr": 0.00816326530612245,
        "position": 10.681632653061225,
        "prevClicks": 3,
        "prevImpressions": 230,
        "clicksChange": -33.33333333333333,
        "impressionsChange": 6.521739130434782
      },
      {
        "url": "https://blog.octanesolutions.com.au/beyond-dashboards-how-agentic-ai-and-enterprise-data-are-powering-the-systems-of-intelligence",
        "title": "Beyond Dashboards How Agentic AI and Enterprise Data Are Powering the Systems of Intelligence",
        "clicks": 2,
        "impressions": 124,
        "ctr": 0.016129032258064516,
        "position": 11.991935483870968,
        "prevClicks": 0,
        "prevImpressions": 49,
        "clicksChange": 100,
        "impressionsChange": 153.0612244897959
      },
      {
        "url": "https://blog.octanesolutions.com.au/planning-analytics-workspace-local-distributed",
        "title": "Planning Analytics Workspace Local Distributed",
        "clicks": 2,
        "impressions": 93,
        "ctr": 0.021505376344086023,
        "position": 21.333333333333332,
        "prevClicks": 1,
        "prevImpressions": 103,
        "clicksChange": 100,
        "impressionsChange": -9.70873786407767
      },
      {
        "url": "https://blog.octanesolutions.com.au/best-practices-for-maximumports-in-tm1-avoiding-paw-connection-failures",
        "title": "Best Practices for Maximumports in TM1 Avoiding PAW Connection Failures",
        "clicks": 2,
        "impressions": 82,
        "ctr": 0.024390243902439025,
        "position": 11.841463414634147,
        "prevClicks": 0,
        "prevImpressions": 43,
        "clicksChange": 100,
        "impressionsChange": 90.69767441860465
      },
      {
        "url": "https://blog.octanesolutions.com.au/using-rules-and-feeders",
        "title": "Using Rules and Feeders",
        "clicks": 2,
        "impressions": 37,
        "ctr": 0.05405405405405406,
        "position": 14.594594594594595,
        "prevClicks": 1,
        "prevImpressions": 23,
        "clicksChange": 100,
        "impressionsChange": 60.86956521739131
      },
      {
        "url": "https://blog.octanesolutions.com.au/mastering-mdx-in-ibm-planning-analytics-workspace?hs_amp=true",
        "title": "Mastering Mdx in IBM Planning Analytics Workspace?hs Amp=true",
        "clicks": 2,
        "impressions": 3,
        "ctr": 0.6666666666666666,
        "position": 6.333333333333333,
        "prevClicks": 0,
        "prevImpressions": 3,
        "clicksChange": 100,
        "impressionsChange": 0
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-project-bob-the-beginning-of-enterprise-grade-agentic-software-development",
        "title": "IBM Project Bob the Beginning of Enterprise Grade Agentic Software Development",
        "clicks": 1,
        "impressions": 1076,
        "ctr": 0.0009293680297397769,
        "position": 9.262081784386616,
        "prevClicks": 1,
        "prevImpressions": 1140,
        "clicksChange": 0,
        "impressionsChange": -5.614035087719298
      },
      {
        "url": "https://blog.octanesolutions.com.au/mastering-tm1distinct-the-smart-way-to-clean-up-your-mdx-subsets",
        "title": "Mastering Tm1distinct the Smart Way to Clean Up Your Mdx Subsets",
        "clicks": 1,
        "impressions": 742,
        "ctr": 0.0013477088948787063,
        "position": 7.522911051212938,
        "prevClicks": 0,
        "prevImpressions": 112,
        "clicksChange": 100,
        "impressionsChange": 562.5
      },
      {
        "url": "https://blog.octanesolutions.com.au/take-complexity-out-of-excel-and-systemize-your-data-with-ibm-cognos-tm1-and-planning-analytics",
        "title": "Take Complexity Out of Excel and Systemize Your Data With IBM Cognos TM1 and Planning Analytics",
        "clicks": 1,
        "impressions": 644,
        "ctr": 0.0015527950310559005,
        "position": 14.236024844720497,
        "prevClicks": 2,
        "prevImpressions": 570,
        "clicksChange": -50,
        "impressionsChange": 12.982456140350877
      },
      {
        "url": "https://blog.octanesolutions.com.au/agentic-ai-in-finance-tm1-why-everyones-suddenly-talking-about-it",
        "title": "Agentic AI in Finance TM1 Why Everyones Suddenly Talking About It",
        "clicks": 1,
        "impressions": 308,
        "ctr": 0.003246753246753247,
        "position": 23.4025974025974,
        "prevClicks": 0,
        "prevImpressions": 279,
        "clicksChange": 100,
        "impressionsChange": 10.39426523297491
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-planning-analytics-for-excel-bug-and-its-fix",
        "title": "IBM Planning Analytics for Excel Bug and Its Fix",
        "clicks": 1,
        "impressions": 292,
        "ctr": 0.003424657534246575,
        "position": 11.006849315068493,
        "prevClicks": 3,
        "prevImpressions": 246,
        "clicksChange": -66.66666666666666,
        "impressionsChange": 18.69918699186992
      },
      {
        "url": "https://blog.octanesolutions.com.au/the-cfos-ai-playbook-from-ah-ha-to-acceleration",
        "title": "the Cfos AI Playbook From Ah Ha to Acceleration",
        "clicks": 1,
        "impressions": 168,
        "ctr": 0.005952380952380952,
        "position": 27.69047619047619,
        "prevClicks": 2,
        "prevImpressions": 89,
        "clicksChange": -50,
        "impressionsChange": 88.76404494382022
      },
      {
        "url": "https://blog.octanesolutions.com.au/power-bi-and-tm1",
        "title": "Power BI and TM1",
        "clicks": 1,
        "impressions": 154,
        "ctr": 0.006493506493506494,
        "position": 24.318181818181817,
        "prevClicks": 0,
        "prevImpressions": 133,
        "clicksChange": 100,
        "impressionsChange": 15.789473684210526
      }
    ]
  },
  "24h": {
    "clicks": 62,
    "impressions": 23832,
    "blogCount": 231,
    "topBlogs": [
      {
        "url": "https://blog.octanesolutions.com.au/chatgpt-for-enterprise-reimagine",
        "title": "Chatgpt for Enterprise Reimagine",
        "clicks": 4,
        "impressions": 668,
        "ctr": 0.005988023952095809,
        "position": 8.905688622754491,
        "prevClicks": 2,
        "prevImpressions": 472,
        "clicksChange": 100,
        "impressionsChange": 41.52542372881356
      },
      {
        "url": "https://blog.octanesolutions.com.au/the-ultimate-ibm-planning-analytics-tm1-training-roadmap-for-beginners",
        "title": "the Ultimate IBM Planning Analytics TM1 Training Roadmap for Beginners",
        "clicks": 4,
        "impressions": 290,
        "ctr": 0.013793103448275862,
        "position": 15.089655172413794,
        "prevClicks": 3,
        "prevImpressions": 320,
        "clicksChange": 33.33333333333333,
        "impressionsChange": -9.375
      },
      {
        "url": "https://blog.octanesolutions.com.au/cognos-analytics-11.0.11.0-is-now-available-for-download",
        "title": "Cognos Analytics 11.0.11.0 is Now Available for Download",
        "clicks": 4,
        "impressions": 158,
        "ctr": 0.02531645569620253,
        "position": 9.468354430379748,
        "prevClicks": 3,
        "prevImpressions": 130,
        "clicksChange": 33.33333333333333,
        "impressionsChange": 21.53846153846154
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-planning-analytics-tm1-anaplan-an-ernest-comparison",
        "title": "IBM Planning Analytics TM1 Anaplan An Ernest Comparison",
        "clicks": 3,
        "impressions": 100,
        "ctr": 0.03,
        "position": 23.69,
        "prevClicks": 1,
        "prevImpressions": 93,
        "clicksChange": 200,
        "impressionsChange": 7.526881720430108
      },
      {
        "url": "https://blog.octanesolutions.com.au/mastering-mdx-in-ibm-planning-analytics-workspace",
        "title": "Mastering Mdx in IBM Planning Analytics Workspace",
        "clicks": 3,
        "impressions": 99,
        "ctr": 0.030303030303030304,
        "position": 15.575757575757576,
        "prevClicks": 0,
        "prevImpressions": 281,
        "clicksChange": 100,
        "impressionsChange": -64.76868327402136
      },
      {
        "url": "https://blog.octanesolutions.com.au/a-tm1-guide-on-how-to-for-dummies",
        "title": "a TM1 Guide on How to for Dummies",
        "clicks": 2,
        "impressions": 3642,
        "ctr": 0.0005491488193300384,
        "position": 6.607907742998353,
        "prevClicks": 5,
        "prevImpressions": 3179,
        "clicksChange": -60,
        "impressionsChange": 14.564328405158856
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-watsonx-orchestrate-use-cases",
        "title": "IBM Watsonx Orchestrate Use Cases",
        "clicks": 2,
        "impressions": 623,
        "ctr": 0.0032102728731942215,
        "position": 7.645264847512038,
        "prevClicks": 8,
        "prevImpressions": 629,
        "clicksChange": -75,
        "impressionsChange": -0.9538950715421303
      },
      {
        "url": "https://blog.octanesolutions.com.au/whats-new-in-cognos-analytics-12.1.x",
        "title": "Whats New in Cognos Analytics 12.1.x",
        "clicks": 2,
        "impressions": 245,
        "ctr": 0.00816326530612245,
        "position": 10.681632653061225,
        "prevClicks": 3,
        "prevImpressions": 230,
        "clicksChange": -33.33333333333333,
        "impressionsChange": 6.521739130434782
      },
      {
        "url": "https://blog.octanesolutions.com.au/beyond-dashboards-how-agentic-ai-and-enterprise-data-are-powering-the-systems-of-intelligence",
        "title": "Beyond Dashboards How Agentic AI and Enterprise Data Are Powering the Systems of Intelligence",
        "clicks": 2,
        "impressions": 124,
        "ctr": 0.016129032258064516,
        "position": 11.991935483870968,
        "prevClicks": 0,
        "prevImpressions": 49,
        "clicksChange": 100,
        "impressionsChange": 153.0612244897959
      },
      {
        "url": "https://blog.octanesolutions.com.au/planning-analytics-workspace-local-distributed",
        "title": "Planning Analytics Workspace Local Distributed",
        "clicks": 2,
        "impressions": 93,
        "ctr": 0.021505376344086023,
        "position": 21.333333333333332,
        "prevClicks": 1,
        "prevImpressions": 103,
        "clicksChange": 100,
        "impressionsChange": -9.70873786407767
      },
      {
        "url": "https://blog.octanesolutions.com.au/best-practices-for-maximumports-in-tm1-avoiding-paw-connection-failures",
        "title": "Best Practices for Maximumports in TM1 Avoiding PAW Connection Failures",
        "clicks": 2,
        "impressions": 82,
        "ctr": 0.024390243902439025,
        "position": 11.841463414634147,
        "prevClicks": 0,
        "prevImpressions": 43,
        "clicksChange": 100,
        "impressionsChange": 90.69767441860465
      },
      {
        "url": "https://blog.octanesolutions.com.au/using-rules-and-feeders",
        "title": "Using Rules and Feeders",
        "clicks": 2,
        "impressions": 37,
        "ctr": 0.05405405405405406,
        "position": 14.594594594594595,
        "prevClicks": 1,
        "prevImpressions": 23,
        "clicksChange": 100,
        "impressionsChange": 60.86956521739131
      },
      {
        "url": "https://blog.octanesolutions.com.au/mastering-mdx-in-ibm-planning-analytics-workspace?hs_amp=true",
        "title": "Mastering Mdx in IBM Planning Analytics Workspace?hs Amp=true",
        "clicks": 2,
        "impressions": 3,
        "ctr": 0.6666666666666666,
        "position": 6.333333333333333,
        "prevClicks": 0,
        "prevImpressions": 3,
        "clicksChange": 100,
        "impressionsChange": 0
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-project-bob-the-beginning-of-enterprise-grade-agentic-software-development",
        "title": "IBM Project Bob the Beginning of Enterprise Grade Agentic Software Development",
        "clicks": 1,
        "impressions": 1076,
        "ctr": 0.0009293680297397769,
        "position": 9.262081784386616,
        "prevClicks": 1,
        "prevImpressions": 1140,
        "clicksChange": 0,
        "impressionsChange": -5.614035087719298
      },
      {
        "url": "https://blog.octanesolutions.com.au/mastering-tm1distinct-the-smart-way-to-clean-up-your-mdx-subsets",
        "title": "Mastering Tm1distinct the Smart Way to Clean Up Your Mdx Subsets",
        "clicks": 1,
        "impressions": 742,
        "ctr": 0.0013477088948787063,
        "position": 7.522911051212938,
        "prevClicks": 0,
        "prevImpressions": 112,
        "clicksChange": 100,
        "impressionsChange": 562.5
      },
      {
        "url": "https://blog.octanesolutions.com.au/take-complexity-out-of-excel-and-systemize-your-data-with-ibm-cognos-tm1-and-planning-analytics",
        "title": "Take Complexity Out of Excel and Systemize Your Data With IBM Cognos TM1 and Planning Analytics",
        "clicks": 1,
        "impressions": 644,
        "ctr": 0.0015527950310559005,
        "position": 14.236024844720497,
        "prevClicks": 2,
        "prevImpressions": 570,
        "clicksChange": -50,
        "impressionsChange": 12.982456140350877
      },
      {
        "url": "https://blog.octanesolutions.com.au/agentic-ai-in-finance-tm1-why-everyones-suddenly-talking-about-it",
        "title": "Agentic AI in Finance TM1 Why Everyones Suddenly Talking About It",
        "clicks": 1,
        "impressions": 308,
        "ctr": 0.003246753246753247,
        "position": 23.4025974025974,
        "prevClicks": 0,
        "prevImpressions": 279,
        "clicksChange": 100,
        "impressionsChange": 10.39426523297491
      },
      {
        "url": "https://blog.octanesolutions.com.au/ibm-planning-analytics-for-excel-bug-and-its-fix",
        "title": "IBM Planning Analytics for Excel Bug and Its Fix",
        "clicks": 1,
        "impressions": 292,
        "ctr": 0.003424657534246575,
        "position": 11.006849315068493,
        "prevClicks": 3,
        "prevImpressions": 246,
        "clicksChange": -66.66666666666666,
        "impressionsChange": 18.69918699186992
      },
      {
        "url": "https://blog.octanesolutions.com.au/the-cfos-ai-playbook-from-ah-ha-to-acceleration",
        "title": "the Cfos AI Playbook From Ah Ha to Acceleration",
        "clicks": 1,
        "impressions": 168,
        "ctr": 0.005952380952380952,
        "position": 27.69047619047619,
        "prevClicks": 2,
        "prevImpressions": 89,
        "clicksChange": -50,
        "impressionsChange": 88.76404494382022
      },
      {
        "url": "https://blog.octanesolutions.com.au/power-bi-and-tm1",
        "title": "Power BI and TM1",
        "clicks": 1,
        "impressions": 154,
        "ctr": 0.006493506493506494,
        "position": 24.318181818181817,
        "prevClicks": 0,
        "prevImpressions": 133,
        "clicksChange": 100,
        "impressionsChange": 15.789473684210526
      }
    ]
  }
};

function parseCookies(cookieHeader) {
  const list = {};
  if (!cookieHeader) return list;
  cookieHeader.split(';').forEach(cookie => {
    const parts = cookie.split('=');
    if (parts.length >= 2) {
      list[parts[0].trim()] = decodeURIComponent(parts.slice(1).join('=').trim());
    }
  });
  return list;
}

function verifySessionToken(token) {
  if (!token || typeof token !== 'string' || !token.includes('.')) return false;
  const parts = token.split('.');
  if (parts.length !== 2) return false;
  const [payloadB64, signatureB64] = parts;

  try {
    const expectedSig = crypto.createHmac('sha256', AUTH_SECRET)
      .update(payloadB64)
      .digest('base64url');

    const bufExpected = Buffer.from(expectedSig);
    const bufActual = Buffer.from(signatureB64);
    if (bufExpected.length !== bufActual.length) return false;
    if (!crypto.timingSafeEqual(bufExpected, bufActual)) return false;

    const payload = JSON.parse(Buffer.from(payloadB64, 'base64url').toString('utf8'));
    if (!payload.authenticated || typeof payload.exp !== 'number') return false;
    if (Date.now() > payload.exp) return false;

    return true;
  } catch (e) {
    return false;
  }
}

module.exports = async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const cookies = parseCookies(req.headers.cookie);
  const sessionToken = cookies['octane_session'];

  // Support internal API calls with session or local development
  if (sessionToken && !verifySessionToken(sessionToken)) {
    return res.status(401).json({ error: 'Unauthorized: Session required' });
  }

  const rawPeriod = (req.query && req.query.period) ? req.query.period.toLowerCase() : 'last90';
  let key = '90d';
  if (rawPeriod.includes('30') || rawPeriod.includes('month')) key = '30d';
  else if (rawPeriod.includes('7') || rawPeriod.includes('week')) key = '7d';
  else if (rawPeriod.includes('24') || rawPeriod.includes('day') || rawPeriod.includes('today')) key = '24h';

  const selectedData = BLOG_DATASETS[key] || BLOG_DATASETS['90d'];

  return res.status(200).json({
    success: true,
    period: rawPeriod,
    timeframeKey: key,
    summary: {
      totalVisits: selectedData.clicks,
      totalImpressions: selectedData.impressions,
      activeBlogsCount: selectedData.blogCount,
      avgCtr: selectedData.impressions > 0 ? (selectedData.clicks / selectedData.impressions) : 0
    },
    blogs: selectedData.topBlogs,
    timestamp: Date.now()
  });
};
