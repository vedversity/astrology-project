// Wording for the free reference pages: Rashi-Nakshatra, names by nakshatra,
// planets in houses, dosha guides and city Panchang pages.
//
// These pages follow the keyword map in the Growth Blueprint. Each answers the
// search query in its first two sentences, then gives the detail.
// Rule for the dosha guides: explain, never frighten, and always give the
// conditions under which a dosha does not apply.

import type { Lang } from "./site";

type Qa = { q: string; a: string };
type DoshaGuide = {
  name: string;
  title: string;
  description: string;
  answer: string;
  sections: { h: string; p: string[] }[];
  faqs: Qa[];
};
export const DOSHA_SLUGS = ["manglik", "kaal-sarp", "sade-sati", "gandmool"] as const;
export type DoshaSlug = (typeof DOSHA_SLUGS)[number];

const hi = {
  crumbs: { home: "मुख्य पेज", naam: "नक्षत्र से नाम", grah: "ग्रह और भाव", dosh: "दोष मार्गदर्शिका", panchang: "पंचांग" },

  tools: {
    title: "आज क्या देखना चाहेंगे?",
    items: [
      { href: "/rashi-nakshatra", title: "राशि और नक्षत्र", text: "जन्म तिथि से मुफ्त जानें" },
      { href: "/panchang", title: "आज का पंचांग", text: "तिथि, राहु काल" },
      { href: "/naam", title: "नक्षत्र से नाम", text: "बच्चों के नाम, अर्थ सहित" },
      { href: "/dosh", title: "दोष मार्गदर्शिका", text: "मांगलिक, साढ़ेसाती" },
      { href: "/grah", title: "ग्रह और भाव", text: "12 भावों में ग्रहों का फल" },
      { href: "/janam-patrika", title: "जन्म पत्रिका PDF", text: "सैंपल और मूल्य" },
    ],
  },

  cta: { title: "अपनी कुंडली में यह सब देखें", text: "जन्म तिथि, समय और स्थान डालें और अपनी राशि, नक्षत्र और नाम अक्षर मुफ्त देखें।", button: "मुफ्त झलक देखें" },

  rashi: {
    title: "राशि और नक्षत्र कैसे जानें — जन्म तिथि से मुफ्त",
    description: "जन्म तिथि, समय और स्थान से अपनी जन्म राशि, नक्षत्र, चरण और नाम का अक्षर मुफ्त जानें। लॉगिन ज़रूरी नहीं।",
    h1: "अपनी राशि और नक्षत्र जानें",
    h2: "Rashi & Nakshatra calculator",
    answer: "आपकी जन्म राशि वह राशि है जिसमें जन्म के समय चंद्रमा था, और जन्म नक्षत्र वह नक्षत्र है जिसमें चंद्रमा था। नीचे जन्म की जानकारी भरें और दोनों तुरंत देखें।",
    sections: [
      { h: "राशि और सूर्य राशि में क्या अंतर है?", p: ["वैदिक ज्योतिष में ‘राशि’ का अर्थ चंद्र राशि है। पश्चिमी पद्धति की ‘सन साइन’ जन्म के महीने से तय होती है, जबकि चंद्र राशि लगभग सवा दो दिन में बदल जाती है, इसलिए जन्म की सही तिथि और समय चाहिए।"] },
      { h: "नक्षत्र और चरण क्या हैं?", p: ["राशिचक्र 27 नक्षत्रों में बँटा है और हर नक्षत्र के चार चरण होते हैं। नामकरण का अक्षर, विंशोत्तरी दशा और गुण मिलान, तीनों जन्म नक्षत्र से निकलते हैं।"] },
      { h: "गणना कैसे होती है?", p: ["चंद्रमा की स्थिति स्विस एफेमेरिस और लाहिरी अयनांश से निकाली जाती है। यही पद्धति भारत के अधिकांश पंचांगों में प्रयुक्त होती है।"] },
    ],
    faqs: [
      { q: "जन्म समय नहीं पता तो राशि कैसे जानें?", a: "‘समय ठीक से नहीं पता’ चुनें। गणना दोपहर 12 बजे से होगी। यदि उस दिन चंद्रमा ने राशि या नक्षत्र बदला था तो हम आपको बता देंगे।" },
      { q: "नाम से राशि और जन्म राशि अलग क्यों आती हैं?", a: "नाम राशि नाम के पहले अक्षर से निकलती है और जन्म राशि चंद्रमा की स्थिति से। ज्योतिषीय गणना के लिए जन्म राशि ही मानी जाती है।" },
      { q: "क्या यह सच में मुफ्त है?", a: "हाँ। राशि, नक्षत्र, चरण और नाम अक्षर हमेशा मुफ्त हैं। विस्तृत जन्म पत्रिका PDF वैकल्पिक है।" },
    ] as Qa[],
  },

  naam: {
    indexTitle: "नक्षत्र के अनुसार बच्चों के नाम — 27 नक्षत्र",
    indexDescription: "हर नक्षत्र के चारों चरणों के नाम अक्षर और उनसे शुरू होने वाले बच्चों के नाम, अर्थ सहित। लड़के और लड़कियों दोनों के लिए।",
    indexH1: "नक्षत्र के अनुसार बच्चों के नाम",
    indexAnswer: "नामकरण में बच्चे का नाम जन्म नक्षत्र के चरण के अक्षर से रखा जाता है। नीचे अपना नक्षत्र चुनें और उसके चारों अक्षर तथा नाम देखें।",
    unknown: "नक्षत्र नहीं पता? जन्म तिथि से मुफ्त जानें →",
    title: "{name} नक्षत्र के नाम — अक्षर {letters}",
    description: "{name} नक्षत्र में जन्मे बच्चों के नाम अक्षर {letters} और इनसे शुरू होने वाले लड़के-लड़कियों के नाम, अर्थ और नामांक सहित।",
    h1: "{name} नक्षत्र में जन्मे बच्चों के नाम",
    h2: "{name} Nakshatra baby names",
    answer: "{name} नक्षत्र के नाम अक्षर {letters} हैं। जन्म जिस चरण में हुआ हो, उसी चरण का अक्षर सबसे उत्तम माना जाता है; नक्षत्र का कोई भी अक्षर मान्य है।",
    lettersTitle: "चारों चरणों के अक्षर",
    pada: "चरण {n}",
    aboutTitle: "{name} नक्षत्र के बारे में",
    facts: { lord: "स्वामी ग्रह", rashi: "राशि", deity: "देवता", symbol: "चिह्न", gana: "गण", yoni: "योनि", nadi: "नाड़ी", tree: "वृक्ष" },
    gandmool: "{name} गण्डमूल नक्षत्र है। परंपरा में 27वें दिन शांति की जाती है; यह सामान्य और सरल विधि है।",
    boys: "लड़कों के नाम",
    girls: "लड़कियों के नाम",
    columns: { name: "नाम", meaning: "अर्थ", letter: "अक्षर", number: "नामांक" },
    sameSound: "समान ध्वनि",
    note: "‘समान ध्वनि’ वाले नाम उसी व्यंजन से शुरू होते हैं पर मात्रा अलग है; परिवार इन्हें भी प्रायः स्वीकार करते हैं। नामांक कैल्डियन पद्धति से है।",
    previous: "पिछला नक्षत्र",
    next: "अगला नक्षत्र",
    premium: "प्रीमियम जन्म पत्रिका में बच्चे के मूलांक और भाग्यांक से मिलाए गए 10 नाम मिलते हैं।",
  },

  grah: {
    indexTitle: "कुंडली के 12 भावों में ग्रहों का फल",
    indexDescription: "सूर्य, चंद्र, मंगल, बुध, गुरु, शुक्र, शनि, राहु और केतु का कुंडली के हर भाव में फल, सरल हिंदी में।",
    indexH1: "कुंडली के भावों में ग्रहों का फल",
    indexAnswer: "कुंडली में हर ग्रह किसी एक भाव में बैठता है और उस भाव के विषयों को अपने स्वभाव से रंग देता है। नीचे ग्रह चुनें और बारहों भावों में उसका फल देखें।",
    title: "{name} का 12 भावों में फल — कुंडली में {name}",
    description: "कुंडली के पहले से बारहवें भाव तक {name} का फल, सरल हिंदी में। साथ में {name} के शुभ दिन, देवता और सात्विक उपाय।",
    h1: "कुंडली के 12 भावों में {name} का फल",
    h2: "{name} in the 12 houses",
    answer: "{name} जिस भाव में बैठा हो, उस भाव के विषयों पर उसका प्रभाव सबसे अधिक दिखता है। नीचे हर भाव का फल दिया है; अंतिम फल राशि, दृष्टि और दशा के साथ मिलाकर देखा जाता है।",
    facts: { day: "दिन", deity: "देवता", mantra: "मंत्र", career: "अनुकूल क्षेत्र" },
    housesTitle: "भाव के अनुसार फल",
    house: "{n} भाव",
    periodTitle: "{name} की महादशा",
    remedyTitle: "सरल उपाय (वैकल्पिक)",
    note: "ये सामान्य फल हैं। आपकी कुंडली में ग्रह की राशि, बल और उस पर पड़ने वाली दृष्टि से फल बदलता है।",
    others: "अन्य ग्रह",
  },

  dosh: {
    indexTitle: "कुंडली के दोष — बिना डर के, सरल भाषा में",
    indexDescription: "मांगलिक, काल सर्प, साढ़ेसाती और गण्डमूल दोष क्या हैं, कैसे पहचाने जाते हैं और किन स्थितियों में नहीं माने जाते।",
    indexH1: "कुंडली के दोष: समझें, डरें नहीं",
    indexAnswer: "दोष कुंडली की एक स्थिति का नाम है, कोई दंड नहीं। लगभग हर दोष के शास्त्रीय परिहार (अपवाद) हैं, जिन्हें जाने बिना निष्कर्ष नहीं निकालना चाहिए।",
    read: "पूरा पढ़ें →",
    checkTitle: "क्या यह आपकी कुंडली में है?",
    checkText: "हमारी जन्म पत्रिका हर दोष की जाँच परिहार नियमों के साथ करती है और साफ़ बताती है: है, नहीं है, या निरस्त।",
    others: "अन्य दोष",
  },

  city: {
    title: "{city} का आज का पंचांग — तिथि, राहु काल",
    description: "{city} के सूर्योदय के अनुसार आज की तिथि, नक्षत्र, योग, करण, सूर्योदय, सूर्यास्त और राहु काल।",
    h1: "{city} का आज का पंचांग",
    h2: "Today's Panchang for {cityEn}",
    answer: "{city} ({state}) के सूर्योदय के अनुसार आज की तिथि, नक्षत्र और राहु काल नीचे दिए हैं। समय {city} की घड़ी के अनुसार हैं।",
    citiesTitle: "अन्य शहरों का पंचांग",
    allCities: "शहर के अनुसार पंचांग",
  },

  positioning: {
    title: "हम क्या करते हैं, और क्या नहीं",
    rows: [
      { them: "प्रति मिनट शुल्क वाली बातचीत", us: "एक बार भुगतान, एक लिखित पत्रिका। कोई मीटर नहीं चलता।" },
      { them: "सैकड़ों पेज जो कोई नहीं पढ़ता", us: "13 पेज जो परिवार सच में पढ़ सके, सरल भाषा में।" },
      { them: "दोष का डर दिखाकर महँगी पूजा और रत्न", us: "हर दोष के साथ परिहार नियम; उपाय वैकल्पिक और सात्विक।" },
      { them: "विज्ञापनों से भरे पेज", us: "पत्रिका और परिणाम के पेजों पर कोई विज्ञापन नहीं।" },
    ],
    themLabel: "आम तौर पर",
    usLabel: "हमारे यहाँ",
  },

  doshas: {
    manglik: {
      name: "मांगलिक दोष",
      title: "मांगलिक दोष कैसे पता करें — और कब नहीं माना जाता",
      description: "मांगलिक दोष क्या है, कुंडली में कैसे देखा जाता है और किन स्थितियों में उसका परिहार हो जाता है। सरल हिंदी में, बिना डर के।",
      answer: "जब मंगल लग्न, चंद्र या शुक्र से पहले, चौथे, सातवें, आठवें या बारहवें भाव में हो, तो कुंडली मांगलिक कही जाती है। यह बहुत आम स्थिति है और कई दशाओं में इसका परिहार हो जाता है।",
      sections: [
        { h: "मांगलिक दोष क्या दर्शाता है", p: ["मंगल ऊर्जा, साहस और स्पष्टवादिता का ग्रह है। इन भावों में वह वैवाहिक जीवन में अधिक ऊर्जा और दृढ़ता लाता है। परंपरा में इसका विचार केवल विवाह-मिलान के समय किया जाता है; जीवन के अन्य क्षेत्रों से इसका संबंध नहीं है।"] },
        { h: "हम इसे कैसे जाँचते हैं", p: ["मंगल की स्थिति तीन स्थानों से देखी जाती है: लग्न, चंद्र और शुक्र। यदि केवल एक या दो से मांगलिक भाव बने, तो उसे आंशिक मांगलिक कहते हैं।", "हम उत्तर भारतीय परंपरा के अनुसार 1, 4, 7, 8 और 12वें भाव गिनते हैं।"] },
        { h: "कब परिहार हो जाता है", p: ["गुरु मंगल के साथ बैठा हो या उस पर दृष्टि डाले।", "मंगल अपनी राशि (मेष, वृश्चिक) या उच्च राशि (मकर) में हो।", "वर और वधू दोनों मांगलिक हों, तो परंपरा में दोष समाप्त माना जाता है।"] },
        { h: "क्या करें", p: ["सबसे पहले पूरी कुंडली में परिहार देखें। यदि दोष बना भी रहे, तो समान योग वाले जीवनसाथी से मिलान इसका सीधा और मान्य समाधान है। केवल इस आधार पर किसी रिश्ते को अस्वीकार करना उचित नहीं।"] },
      ],
      faqs: [
        { q: "क्या मांगलिक की शादी गैर-मांगलिक से हो सकती है?", a: "हाँ, यदि कुंडली में परिहार हो या ज्योतिषी दोनों कुंडलियों का समग्र मिलान अनुकूल पाएँ। निर्णय केवल एक योग पर नहीं टिकता।" },
        { q: "आंशिक मांगलिक क्या होता है?", a: "जब मंगल लग्न, चंद्र और शुक्र में से केवल एक या दो से मांगलिक भाव में हो। यह हल्का रूप है।" },
        { q: "क्या मांगलिक दोष उम्र के साथ समाप्त होता है?", a: "कुछ परंपराएँ 28 वर्ष की आयु के बाद इसका प्रभाव कम मानती हैं। यह मत सभी ज्योतिषियों में समान नहीं है।" },
      ],
    },
    "kaal-sarp": {
      name: "काल सर्प योग",
      title: "काल सर्प दोष क्या है और कैसे पहचानें",
      description: "काल सर्प योग कब बनता है, कब नहीं बनता और इसका वास्तविक अर्थ क्या है। सरल हिंदी में, बिना डर के।",
      answer: "जब सूर्य से शनि तक सातों ग्रह राहु और केतु की धुरी के एक ही ओर हों, तो काल सर्प योग बनता है। यदि एक भी ग्रह दूसरी ओर हो, तो यह योग नहीं बनता।",
      sections: [
        { h: "इसका अर्थ क्या है", p: ["यह योग एकाग्र और दृढ़ स्वभाव देता है: जीवन की ऊर्जा एक दिशा में केंद्रित रहती है। अनेक सफल और प्रसिद्ध व्यक्तियों की कुंडली में यह योग मिलता है।", "प्राचीन मूल ग्रंथों में इसका उल्लेख सीमित है; इसका महत्व बाद की परंपरा में बढ़ा। इसलिए इसे संतुलित दृष्टि से देखना चाहिए।"] },
        { h: "हम इसे कैसे जाँचते हैं", p: ["राहु के अंश से हर ग्रह की दूरी देखी जाती है। सातों ग्रह या तो सभी 180 अंश के भीतर हों, या सभी उसके बाहर, तभी योग माना जाता है।"] },
        { h: "कब नहीं माना जाता", p: ["कोई भी एक ग्रह धुरी के दूसरी ओर हो।", "कुछ परंपराओं में, यदि कोई ग्रह राहु या केतु के साथ उसी राशि में अधिक अंश पर हो, तो योग भंग माना जाता है।"] },
        { h: "क्या करें", p: ["भगवान शिव की उपासना और नियमित दिनचर्या परंपरागत और सरल उपाय हैं। महँगी पूजा आवश्यक नहीं है।"] },
      ],
      faqs: [
        { q: "क्या काल सर्प दोष जीवन भर रहता है?", a: "यह जन्म कुंडली की स्थिति है, इसलिए कुंडली में बनी रहती है। पर इसका प्रभाव पूरी कुंडली के बल और चल रही दशा पर निर्भर करता है।" },
        { q: "काल सर्प योग के कितने प्रकार हैं?", a: "राहु जिस भाव में हो उसके अनुसार परंपरा में बारह नाम दिए गए हैं, जैसे अनंत, कुलिक, वासुकि। मूल शर्त सबमें एक ही है।" },
        { q: "क्या इसकी पूजा अनिवार्य है?", a: "नहीं। उपाय वैकल्पिक हैं। निर्णय अपनी आस्था और परिवार की परंपरा से लें।" },
      ],
    },
    "sade-sati": {
      name: "शनि साढ़ेसाती",
      title: "साढ़ेसाती क्या है — कब शुरू और कब समाप्त होती है",
      description: "शनि की साढ़ेसाती कब लगती है, उसके तीन चरण क्या हैं और इस समय क्या करना चाहिए। सरल हिंदी में, बिना डर के।",
      answer: "जब शनि आपकी जन्म राशि से पिछली राशि, जन्म राशि और अगली राशि से गुज़रता है, तो उस लगभग साढ़े सात वर्ष के समय को साढ़ेसाती कहते हैं। यह हर व्यक्ति के जीवन में दो से तीन बार आती है।",
      sections: [
        { h: "तीन चरण", p: ["पहला चरण: शनि जन्म राशि से बारहवीं राशि में।", "मध्य चरण: शनि जन्म राशि में।", "अंतिम चरण: शनि जन्म राशि से दूसरी राशि में। हर चरण लगभग ढाई वर्ष का होता है।"] },
        { h: "इसका अर्थ क्या है", p: ["शनि अनुशासन, परिश्रम और उत्तरदायित्व का ग्रह है। साढ़ेसाती प्रायः अधिक मेहनत और ज़िम्मेदारी का समय होती है, और इसी समय में लोग जीवन की ठोस नींव भी बनाते हैं।", "कई लोगों को इसी अवधि में पद, संपत्ति और स्थायित्व मिला है। फल कुंडली में शनि के बल पर निर्भर करता है।"] },
        { h: "हम इसे कैसे जाँचते हैं", p: ["शनि की वास्तविक गोचर स्थिति दिन-प्रतिदिन देखी जाती है। वक्री होने पर शनि कुछ महीनों के लिए पिछली राशि में लौट सकता है, इसलिए हम पहली बार निकलने की तिथि और अंतिम रूप से निकलने की तिथि, दोनों बताते हैं।"] },
        { h: "क्या करें", p: ["नियमित दिनचर्या, परिश्रम और बड़ों की सेवा शनि के स्वाभाविक उपाय हैं।", "परंपरा में शनिवार को पीपल के नीचे दीपक जलाना और हनुमान चालीसा का पाठ किया जाता है।"] },
      ],
      faqs: [
        { q: "मेरी साढ़ेसाती चल रही है या नहीं, कैसे पता करूँ?", a: "पहले अपनी जन्म राशि जानें, फिर देखें कि शनि अभी किस राशि में है। यदि वह आपकी राशि से एक पहले, उसी में या एक बाद की राशि में है, तो साढ़ेसाती चल रही है।" },
        { q: "क्या साढ़ेसाती हमेशा कष्ट देती है?", a: "नहीं। यह अधिक परिश्रम और अनुशासन का समय है। जिनकी कुंडली में शनि बली है, उन्हें यह समय उन्नति भी देता है।" },
        { q: "ढैया क्या होती है?", a: "जब शनि जन्म राशि से चौथी या आठवीं राशि में हो, तो लगभग ढाई वर्ष की उस अवधि को ढैया कहते हैं।" },
      ],
    },
    gandmool: {
      name: "गण्डमूल नक्षत्र",
      title: "गण्डमूल नक्षत्र कौन-से हैं और शांति कब करें",
      description: "छह गण्डमूल नक्षत्र, उनके चरणों का अर्थ और 27वें दिन की शांति के बारे में सरल हिंदी में जानकारी।",
      answer: "अश्विनी, आश्लेषा, मघा, ज्येष्ठा, मूल और रेवती, ये छह गण्डमूल नक्षत्र हैं। इनमें जन्म होने पर परंपरा में 27वें दिन, जब चंद्रमा उसी नक्षत्र में लौटता है, शांति की जाती है।",
      sections: [
        { h: "गण्डमूल क्यों कहते हैं", p: ["ये नक्षत्र वहाँ पड़ते हैं जहाँ राशि और नक्षत्र दोनों एक साथ समाप्त या आरंभ होते हैं, अर्थात जल और अग्नि तत्व की राशियों की संधि पर। इसी संधि को गण्ड कहा गया है।"] },
        { h: "चरण का महत्व", p: ["हर नक्षत्र का केवल संधि वाला चरण ही अधिक महत्व का माना जाता है: अश्विनी, मघा और मूल का पहला चरण; आश्लेषा, ज्येष्ठा और रेवती का चौथा चरण।", "शेष चरणों में जन्म हल्का माना जाता है।"] },
        { h: "शांति क्या है", p: ["यह एक साधारण पूजा है जो जन्म के 27वें दिन की जाती है। इसके बाद इस विषय को पूर्ण माना जाता है। सही मुहूर्त अपने कुल पंडित से निश्चित करें।"] },
        { h: "याद रखें", p: ["इन नक्षत्रों में जन्मे लोग प्रायः तीव्र बुद्धि और नेतृत्व क्षमता वाले होते हैं। अश्विनी गति का, मघा गरिमा का, मूल गहरी खोज का और रेवती कोमल हृदय का नक्षत्र है।"] },
      ],
      faqs: [
        { q: "गण्डमूल शांति कब करनी चाहिए?", a: "जन्म के 27वें दिन, जब चंद्रमा पुनः जन्म नक्षत्र में आता है। हमारी पत्रिका में यह तिथि दी जाती है।" },
        { q: "यदि 27वें दिन शांति न हो पाए तो?", a: "परंपरा में अगली बार जब चंद्रमा उसी नक्षत्र में आए, तब शांति की जा सकती है। अपने पंडित से पूछें।" },
        { q: "क्या नामकरण शांति से पहले हो सकता है?", a: "अधिकांश परिवार शांति के बाद नामकरण करते हैं। यह परिवार की परंपरा पर निर्भर है।" },
      ],
    },
  } as Record<DoshaSlug, DoshaGuide>,
};

const en: typeof hi = {
  crumbs: { home: "Home", naam: "Names by Nakshatra", grah: "Planets in Houses", dosh: "Dosha Guide", panchang: "Panchang" },

  tools: {
    title: "What would you like to see today?",
    items: [
      { href: "/rashi-nakshatra", title: "Rashi & Nakshatra", text: "Free, from the birth date" },
      { href: "/panchang", title: "Today's Panchang", text: "Tithi, Rahu Kaal" },
      { href: "/naam", title: "Names by Nakshatra", text: "Baby names with meanings" },
      { href: "/dosh", title: "Dosha Guide", text: "Manglik, Sade Sati" },
      { href: "/grah", title: "Planets in Houses", text: "Results in all 12 houses" },
      { href: "/janam-patrika", title: "Janam Patrika PDF", text: "Samples and prices" },
    ],
  },

  cta: { title: "See all this in your own chart", text: "Enter the date, time and place of birth to see your Rashi, Nakshatra and name letters free.", button: "See free preview" },

  rashi: {
    title: "Find your Rashi and Nakshatra — free, by date of birth",
    description: "Find your Janma Rashi, Nakshatra, pada and name letter free from the date, time and place of birth. No login needed.",
    h1: "Find your Rashi and Nakshatra",
    h2: "राशि और नक्षत्र कैलकुलेटर",
    answer: "Your Janma Rashi is the sign the Moon was in when you were born, and your Janma Nakshatra is the star it was in. Fill in the birth details below to see both at once.",
    sections: [
      { h: "How is the Rashi different from the Sun sign?", p: ["In Vedic astrology ‘Rashi’ means the Moon sign. The Western ‘Sun sign’ depends only on the month of birth, while the Moon changes sign about every two and a quarter days, so the exact date and time of birth are needed."] },
      { h: "What are the Nakshatra and pada?", p: ["The zodiac is divided into 27 nakshatras, each with four padas (quarters). The naming letter, the Vimshottari dasha and Guna matching all come from the birth nakshatra."] },
      { h: "How is it calculated?", p: ["The Moon's position is worked out with the Swiss Ephemeris and the Lahiri ayanamsa, the method used by most almanacs in India."] },
    ],
    faqs: [
      { q: "How do I find my Rashi without the birth time?", a: "Tick ‘I'm not sure of the exact time’. The calculation uses 12 noon. If the Moon changed sign or nakshatra on that day, we tell you." },
      { q: "Why does my name Rashi differ from my Janma Rashi?", a: "The name Rashi comes from the first letter of the name; the Janma Rashi comes from the Moon's position. Astrological calculation uses the Janma Rashi." },
      { q: "Is it really free?", a: "Yes. Rashi, Nakshatra, pada and name letters are always free. The detailed Janam Patrika PDF is optional." },
    ],
  },

  naam: {
    indexTitle: "Baby names by Nakshatra — all 27 Nakshatras",
    indexDescription: "The naming letters for all four padas of each nakshatra and baby names that begin with them, with meanings. For boys and girls.",
    indexH1: "Baby names by Nakshatra",
    indexAnswer: "At the Namkaran a child is named from the letter of the pada of the birth nakshatra. Choose a nakshatra below to see its four letters and the names.",
    unknown: "Don't know the nakshatra? Find it free from the birth date →",
    title: "{name} Nakshatra baby names",
    description: "{name} Nakshatra naming letters ({letters}) and boy and girl names that begin with them, with meanings.",
    h1: "Baby names for {name} Nakshatra",
    h2: "{name} नक्षत्र के नाम",
    answer: "The naming letters of {name} Nakshatra are {letters}. The letter of the pada of birth is the first choice; any letter of the nakshatra is acceptable.",
    lettersTitle: "Letters of the four padas",
    pada: "Pada {n}",
    aboutTitle: "About {name} Nakshatra",
    facts: { lord: "Ruling planet", rashi: "Rashi", deity: "Deity", symbol: "Symbol", gana: "Gana", yoni: "Yoni", nadi: "Nadi", tree: "Tree" },
    gandmool: "{name} is a Gandmool nakshatra. By tradition a Shanti is done on the 27th day; it is an ordinary, simple ritual.",
    boys: "Names for boys",
    girls: "Names for girls",
    columns: { name: "Name", meaning: "Meaning", letter: "Letter", number: "Name no." },
    sameSound: "same sound",
    note: "Names marked ‘same sound’ begin with the same consonant but a different vowel; families usually accept these too. Name numbers use the Chaldean system.",
    previous: "Previous nakshatra",
    next: "Next nakshatra",
    premium: "The Premium Janam Patrika gives 10 names matched to the child's Mulank and Bhagyank.",
  },

  grah: {
    indexTitle: "Planets in the 12 houses of the Kundli",
    indexDescription: "What the Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu and Ketu mean in each house of the Kundli, in plain words.",
    indexH1: "Planets in the houses of the Kundli",
    indexAnswer: "In a Kundli each planet sits in one house and colours the matters of that house with its own nature. Choose a planet below to see what it means in all twelve houses.",
    title: "{name} in the 12 houses of the Kundli",
    description: "What {name} means in each house of the Kundli, from the 1st to the 12th, with its day, deity and gentle remedies.",
    h1: "{name} in the 12 houses of the Kundli",
    h2: "12 भावों में {name} का फल",
    answer: "{name} shows its influence most in the matters of the house it occupies. Each house is described below; the final reading also weighs the sign, the aspects and the dasha.",
    facts: { day: "Day", deity: "Deity", mantra: "Mantra", career: "Suited fields" },
    housesTitle: "Results by house",
    house: "{n} house",
    periodTitle: "The {name} Mahadasha",
    remedyTitle: "Simple remedies (optional)",
    note: "These are general results. In your own chart the planet's sign, strength and the aspects on it change the reading.",
    others: "Other planets",
  },

  dosh: {
    indexTitle: "Doshas in the Kundli — explained without fear",
    indexDescription: "What Manglik, Kaal Sarp, Sade Sati and Gandmool are, how they are identified and when they do not apply.",
    indexH1: "Doshas in the Kundli: understand them, don't fear them",
    indexAnswer: "A dosha is the name of a pattern in the chart, not a punishment. Almost every dosha has classical exceptions (parihar), and no conclusion should be drawn without checking them.",
    read: "Read more →",
    checkTitle: "Is it in your chart?",
    checkText: "Our Janam Patrika checks every dosha together with its cancellation rules and says plainly: present, not present, or cancelled.",
    others: "Other doshas",
  },

  city: {
    title: "Today's Panchang for {city} — tithi, Rahu Kaal",
    description: "Today's tithi, nakshatra, yoga, karana, sunrise, sunset and Rahu Kaal, worked out from sunrise in {city}.",
    h1: "Today's Panchang for {city}",
    h2: "{cityHi} का आज का पंचांग",
    answer: "Today's tithi, nakshatra and Rahu Kaal for {city} ({state}) are given below, worked out from sunrise there. Times are by the clock in {city}.",
    citiesTitle: "Panchang for other cities",
    allCities: "Panchang by city",
  },

  positioning: {
    title: "What we do, and what we don't",
    rows: [
      { them: "Chat charged by the minute", us: "One payment, one written Patrika. No meter running." },
      { them: "Hundreds of pages nobody reads", us: "13 pages a family will actually read, in plain words." },
      { them: "Fear of a dosha, then costly pujas and gems", us: "Every dosha with its cancellation rules; remedies optional and gentle." },
      { them: "Pages crowded with ads", us: "No ads on the Patrika or result pages." },
    ],
    themLabel: "Commonly",
    usLabel: "With us",
  },

  doshas: {
    manglik: {
      name: "Manglik Dosha",
      title: "How to check Manglik Dosha — and when it does not apply",
      description: "What Manglik Dosha is, how it is read in the Kundli and the conditions under which it is cancelled. In plain words, without fear.",
      answer: "A chart is called Manglik when Mars is in the 1st, 4th, 7th, 8th or 12th house counted from the Lagna, the Moon or Venus. It is a very common placement, and in many charts it is cancelled.",
      sections: [
        { h: "What it shows", p: ["Mars is the planet of energy, courage and directness. In these houses it brings extra energy and firmness to married life. By tradition it is considered only at the time of marriage matching; it has nothing to do with other areas of life."] },
        { h: "How we check it", p: ["Mars is looked at from three places: the Lagna, the Moon and Venus. If it falls in a Manglik house from only one or two of them, it is called Anshik (partial) Manglik.", "We follow the North Indian convention of houses 1, 4, 7, 8 and 12."] },
        { h: "When it is cancelled", p: ["Jupiter sits with Mars or aspects it.", "Mars is in its own sign (Aries, Scorpio) or its exaltation sign (Capricorn).", "Both the bride and the groom are Manglik, in which case tradition holds the dosha to be removed."] },
        { h: "What to do", p: ["First check the whole chart for a cancellation. If the dosha remains, matching with a partner who has a similar placement is the direct, accepted answer. Rejecting a match on this ground alone is not justified."] },
      ],
      faqs: [
        { q: "Can a Manglik marry a non-Manglik?", a: "Yes, if the chart has a cancellation or an astrologer finds the overall match of the two charts favourable. The decision does not rest on one placement." },
        { q: "What is Anshik Manglik?", a: "When Mars is in a Manglik house from only one or two of the Lagna, the Moon and Venus. It is the mild form." },
        { q: "Does Manglik Dosha end with age?", a: "Some traditions hold that its effect lessens after the age of 28. Not all astrologers agree on this." },
      ],
    },
    "kaal-sarp": {
      name: "Kaal Sarp Yoga",
      title: "What is Kaal Sarp Dosha and how is it identified",
      description: "When Kaal Sarp Yoga forms, when it does not, and what it really means. In plain words, without fear.",
      answer: "Kaal Sarp Yoga forms when all seven planets, from the Sun to Saturn, lie on one side of the Rahu-Ketu axis. If even one planet is on the other side, the yoga does not form.",
      sections: [
        { h: "What it means", p: ["This yoga gives a focused, determined nature: life's energy is concentrated in one direction. It is found in the charts of many successful and well-known people.", "The oldest classical texts say little about it; its importance grew in later tradition. It deserves a balanced view."] },
        { h: "How we check it", p: ["Each planet's distance from Rahu is measured. The yoga is counted only when all seven planets are within 180 degrees, or all are outside it."] },
        { h: "When it does not apply", p: ["Any one planet is on the other side of the axis.", "In some traditions, the yoga is broken if a planet shares a sign with Rahu or Ketu at a higher degree."] },
        { h: "What to do", p: ["Worship of Lord Shiva and a regular routine are the traditional, simple remedies. A costly puja is not necessary."] },
      ],
      faqs: [
        { q: "Does Kaal Sarp Dosha last a lifetime?", a: "It is a pattern of the birth chart, so it stays in the chart. Its effect depends on the strength of the whole chart and the dasha running." },
        { q: "How many types of Kaal Sarp Yoga are there?", a: "Tradition gives twelve names by the house Rahu occupies, such as Anant, Kulik and Vasuki. The basic condition is the same for all." },
        { q: "Is the puja compulsory?", a: "No. Remedies are optional. Decide by your own faith and your family's tradition." },
      ],
    },
    "sade-sati": {
      name: "Shani Sade Sati",
      title: "What is Sade Sati — when it starts and when it ends",
      description: "When Saturn's Sade Sati begins, its three phases and what to do during it. In plain words, without fear.",
      answer: "Sade Sati is the period of about seven and a half years in which Saturn passes through the sign before your Janma Rashi, the Rashi itself and the sign after it. It comes two or three times in every life.",
      sections: [
        { h: "The three phases", p: ["First phase: Saturn in the 12th sign from the Janma Rashi.", "Peak phase: Saturn in the Janma Rashi.", "Last phase: Saturn in the 2nd sign from the Janma Rashi. Each phase lasts about two and a half years."] },
        { h: "What it means", p: ["Saturn is the planet of discipline, hard work and responsibility. Sade Sati is usually a time of more effort and duty, and it is also when people lay the solid foundations of their lives.", "Many people have gained position, property and stability in this very period. The result depends on Saturn's strength in the chart."] },
        { h: "How we check it", p: ["Saturn's actual transit is followed day by day. When retrograde, Saturn can step back into the previous sign for some months, so we give both the date it first leaves and the date it leaves for good."] },
        { h: "What to do", p: ["A regular routine, hard work and service to elders are Saturn's natural remedies.", "By tradition a lamp is lit under a Peepal tree on Saturdays and the Hanuman Chalisa is recited."] },
      ],
      faqs: [
        { q: "How do I know if my Sade Sati is running?", a: "First find your Janma Rashi, then see which sign Saturn is in now. If it is in the sign before yours, in yours or in the one after, Sade Sati is running." },
        { q: "Is Sade Sati always difficult?", a: "No. It is a time of more work and discipline. For those with a strong Saturn in the chart it also brings advancement." },
        { q: "What is a Dhaiya?", a: "When Saturn is in the 4th or 8th sign from the Janma Rashi, that period of about two and a half years is called a Dhaiya." },
      ],
    },
    gandmool: {
      name: "Gandmool Nakshatra",
      title: "Which are the Gandmool Nakshatras and when is the Shanti done",
      description: "The six Gandmool nakshatras, what their padas mean and the Shanti done on the 27th day, in plain words.",
      answer: "Ashwini, Ashlesha, Magha, Jyeshtha, Mula and Revati are the six Gandmool nakshatras. For a birth in one of them, tradition holds a Shanti on the 27th day, when the Moon returns to the same nakshatra.",
      sections: [
        { h: "Why they are called Gandmool", p: ["These nakshatras fall where a sign and a nakshatra end or begin together, at the junction of the water and fire signs. That junction is called a ganda."] },
        { h: "Why the pada matters", p: ["In each nakshatra only the pada at the junction is given more weight: the first pada of Ashwini, Magha and Mula; the fourth pada of Ashlesha, Jyeshtha and Revati.", "A birth in the other padas is considered mild."] },
        { h: "What the Shanti is", p: ["It is an ordinary puja done on the 27th day after birth. After it the matter is considered settled. Fix the exact muhurat with your family pandit."] },
        { h: "Remember", p: ["People born in these nakshatras are often sharp-minded and capable of leadership. Ashwini is the star of speed, Magha of dignity, Mula of deep inquiry and Revati of a gentle heart."] },
      ],
      faqs: [
        { q: "When should the Gandmool Shanti be done?", a: "On the 27th day after birth, when the Moon returns to the birth nakshatra. Our Patrika gives this date." },
        { q: "What if the Shanti cannot be done on the 27th day?", a: "By tradition it can be done the next time the Moon is in the same nakshatra. Ask your pandit." },
        { q: "Can the Namkaran be held before the Shanti?", a: "Most families hold the Namkaran after the Shanti. It depends on family tradition." },
      ],
    },
  },
};

export function guides(lang: Lang) {
  return lang === "hi" ? hi : en;
}
