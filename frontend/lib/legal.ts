// The four policy pages, in Hindi and English.
//
// IMPORTANT: these are first drafts written to match how the product works.
// Have them checked by a lawyer before launch, then set DRAFT to false to
// remove the notice shown at the top of each page.

import type { Lang } from "./site";

export const DRAFT = true;
export const LAST_UPDATED = "2026-10-04";

export type LegalKey = "privacy" | "terms" | "refund" | "disclaimer";
type Section = { h: string; p: string[] };
type Doc = { title: string; description: string; sections: Section[] };

const hi: Record<LegalKey, Doc> & { draft: string; updated: string } = {
  draft: "यह मसौदा है। लॉन्च से पहले कानूनी समीक्षा होनी बाकी है।",
  updated: "अंतिम अद्यतन",

  privacy: {
    title: "गोपनीयता नीति",
    description: "हम कौन-सी जानकारी लेते हैं, उसका क्या उपयोग होता है और आप उसे कैसे हटवा सकते हैं।",
    sections: [
      {
        h: "हम कौन-सी जानकारी लेते हैं",
        p: [
          "मुफ्त झलक के लिए: जन्म तिथि, जन्म समय, जन्म स्थान, लिंग और (यदि आप दें) नाम।",
          "पत्रिका के ऑर्डर के लिए: पत्रिका पर छपने वाले नाम, गोत्र, कुलदेवी, आपका WhatsApp नंबर और (यदि आप दें) ईमेल।",
          "भुगतान की जानकारी (कार्ड या UPI विवरण) हमारे पास नहीं आती; वह सीधे भुगतान सेवा के पास जाती है।",
        ],
      },
      {
        h: "जानकारी का उपयोग",
        p: [
          "आपकी जानकारी केवल आपकी कुंडली की गणना करने, पत्रिका बनाने और आप तक पहुँचाने के लिए उपयोग होती है।",
          "हम आपकी जानकारी किसी को नहीं बेचते और विज्ञापन के लिए किसी से साझा नहीं करते।",
        ],
      },
      {
        h: "जानकारी कहाँ रहती है",
        p: [
          "फ़ॉर्म में भरी जानकारी आपके अपने फ़ोन या कंप्यूटर में याद रखी जाती है, ताकि दोबारा न भरनी पड़े। इसे आप इसी पेज के नीचे दिए बटन से हटा सकते हैं।",
          "जन्म स्थान की खोज हमारे अपने सर्वर पर होती है; आप जो लिखते हैं वह किसी बाहरी सेवा को नहीं भेजा जाता।",
          "ऑर्डर की जानकारी सुरक्षित (HTTPS) कनेक्शन से भेजी जाती है और उतने ही समय रखी जाती है जितना पत्रिका पहुँचाने और कानूनी अभिलेख के लिए आवश्यक है।",
        ],
      },
      {
        h: "बच्चों की जानकारी",
        p: ["नवजात या नाबालिग की पत्रिका के लिए जानकारी उसके माता-पिता या अभिभावक ही दें। बच्चे की जन्म जानकारी संवेदनशील है और हम उसे उसी सावधानी से रखते हैं।"],
      },
      {
        h: "आपके अधिकार",
        p: [
          "आप कभी भी पूछ सकते हैं कि हमारे पास आपकी कौन-सी जानकारी है, उसे सुधरवा सकते हैं या हटवा सकते हैं।",
          "इसके लिए हमसे संपर्क करें; हम डिजिटल व्यक्तिगत डेटा संरक्षण अधिनियम, 2023 के अनुसार उत्तर देंगे।",
        ],
      },
    ],
  },

  terms: {
    title: "नियम और शर्तें",
    description: "इस वेबसाइट और जन्म पत्रिका सेवा के उपयोग की शर्तें।",
    sections: [
      {
        h: "सेवा क्या है",
        p: [
          "यह वेबसाइट आपकी दी हुई जन्म जानकारी से वैदिक ज्योतिष की गणना करती है और उसके आधार पर जन्म पत्रिका (PDF) तैयार करती है।",
          "मुफ्त झलक निःशुल्क है। विस्तृत पत्रिका सशुल्क है और उसका मूल्य ऑर्डर के समय दिखाया जाता है।",
        ],
      },
      {
        h: "आपकी ज़िम्मेदारी",
        p: [
          "पत्रिका आपकी दी हुई जन्म तिथि, समय और स्थान पर आधारित है। गलत जानकारी से पत्रिका भी गलत बनेगी।",
          "किसी और की जानकारी केवल उसकी सहमति से, या बच्चे के लिए अभिभावक के रूप में, दें।",
        ],
      },
      {
        h: "ज्योतिष की सीमा",
        p: [
          "पत्रिका मार्गदर्शन और सांस्कृतिक उद्देश्य के लिए है। यह चिकित्सा, कानूनी या आर्थिक सलाह नहीं है और किसी परिणाम की गारंटी नहीं देती।",
          "अलग-अलग पंचांग और सॉफ़्टवेयर में गणना की पद्धति के कारण थोड़ा अंतर हो सकता है।",
        ],
      },
      {
        h: "उपयोग की अनुमति",
        p: ["पत्रिका आपके और आपके परिवार के निजी उपयोग के लिए है। इसे बेचना या व्यावसायिक रूप से बाँटना अनुमत नहीं है।"],
      },
      {
        h: "बदलाव",
        p: ["हम समय-समय पर इन शर्तों और मूल्यों को बदल सकते हैं। बदली हुई शर्तें इसी पेज पर दिखाई जाएँगी।"],
      },
    ],
  },

  refund: {
    title: "रिफंड नीति",
    description: "पत्रिका न मिलने या गलत बनने पर क्या होगा।",
    sections: [
      {
        h: "भुगतान से पहले देखें",
        p: ["भुगतान से पहले मुफ्त झलक और सैंपल पेज उपलब्ध हैं, ताकि आप देखकर निर्णय ले सकें।"],
      },
      {
        h: "पूरा पैसा वापस",
        p: [
          "यदि भुगतान के बाद तकनीकी कारण से आपकी पत्रिका नहीं बन पाती या आप तक नहीं पहुँचती, तो पूरा पैसा वापस किया जाएगा।",
          "रिफंड उसी माध्यम में आएगा जिससे भुगतान हुआ था।",
        ],
      },
      {
        h: "जन्म जानकारी में गलती",
        p: ["यदि आपने जन्म तिथि, समय या स्थान गलत भर दिया है, तो हमसे संपर्क करें; सही जानकारी से पत्रिका दोबारा बनाई जा सकती है।"],
      },
      {
        h: "कब रिफंड नहीं",
        p: ["पत्रिका डिजिटल उत्पाद है। सही जानकारी से बनकर मिल जाने के बाद, केवल फलादेश से असहमति के आधार पर रिफंड नहीं दिया जाता।"],
      },
    ],
  },

  disclaimer: {
    title: "अस्वीकरण",
    description: "ज्योतिष मार्गदर्शन है, गारंटी नहीं।",
    sections: [
      {
        h: "मार्गदर्शन, गारंटी नहीं",
        p: [
          "यहाँ दी गई जन्म पत्रिका, पंचांग और अन्य जानकारी मार्गदर्शन और सांस्कृतिक उद्देश्य के लिए है।",
          "ज्योतिष प्रवृत्तियाँ और संभावनाएँ बताता है, निश्चित भविष्य नहीं। जीवन को सबसे अधिक आपके अपने निर्णय, परिश्रम और संस्कार आकार देते हैं।",
        ],
      },
      {
        h: "विशेषज्ञ की सलाह का विकल्प नहीं",
        p: ["स्वास्थ्य, कानून, धन, शिक्षा या विवाह से जुड़े महत्वपूर्ण निर्णय योग्य विशेषज्ञ की सलाह से ही लें।"],
      },
      {
        h: "उपाय वैकल्पिक हैं",
        p: ["पत्रिका में दिए उपाय परंपरा पर आधारित सुझाव हैं और पूरी तरह वैकल्पिक हैं। हम कोई पूजा, रत्न या वस्तु खरीदने का दबाव नहीं डालते।"],
      },
      {
        h: "गणना",
        p: ["गणना स्विस एफेमेरिस और लाहिरी अयनांश से होती है। जन्म समय में कुछ मिनट का अंतर भी लग्न और वर्ग कुंडलियों को बदल सकता है।"],
      },
    ],
  },
};

const en: typeof hi = {
  draft: "This is a draft. It has not yet had a legal review before launch.",
  updated: "Last updated",

  privacy: {
    title: "Privacy Policy",
    description: "What details we take, what they are used for and how you can have them removed.",
    sections: [
      {
        h: "What we collect",
        p: [
          "For the free preview: date of birth, time of birth, place of birth, gender and (if you give it) a name.",
          "For a Patrika order: the names to print, gotra, kuldevi, your WhatsApp number and (if you give it) your email.",
          "Payment details (card or UPI) never reach us; they go directly to the payment service.",
        ],
      },
      {
        h: "How it is used",
        p: [
          "Your details are used only to calculate your chart, prepare the Patrika and deliver it to you.",
          "We never sell your details and do not share them with anyone for advertising.",
        ],
      },
      {
        h: "Where it is kept",
        p: [
          "What you type into the form is remembered on your own phone or computer, so you need not type it again. You can remove it with the button at the bottom of this page.",
          "The birth-place search runs on our own server; what you type is not sent to any outside service.",
          "Order details are sent over a secure (HTTPS) connection and kept only as long as needed to deliver the Patrika and for legal records.",
        ],
      },
      {
        h: "Children's details",
        p: ["Details for a newborn or a minor should be given only by a parent or guardian. A child's birth details are sensitive and we handle them with that care."],
      },
      {
        h: "Your rights",
        p: [
          "You may ask at any time what details we hold about you, and have them corrected or deleted.",
          "Contact us to do so; we will respond as required by the Digital Personal Data Protection Act, 2023.",
        ],
      },
    ],
  },

  terms: {
    title: "Terms and Conditions",
    description: "The terms for using this website and the Janam Patrika service.",
    sections: [
      {
        h: "What the service is",
        p: [
          "This website performs Vedic astrology calculations from the birth details you give and prepares a Janam Patrika (PDF) from them.",
          "The preview is free. The detailed Patrika is paid, and its price is shown when you order.",
        ],
      },
      {
        h: "Your responsibility",
        p: [
          "The Patrika is based on the date, time and place of birth you provide. Incorrect details produce an incorrect Patrika.",
          "Give another person's details only with their consent, or as the guardian of a child.",
        ],
      },
      {
        h: "The limits of astrology",
        p: [
          "The Patrika is for guidance and cultural purposes. It is not medical, legal or financial advice and guarantees no outcome.",
          "Different almanacs and software may differ slightly because of their calculation methods.",
        ],
      },
      {
        h: "Permitted use",
        p: ["The Patrika is for the private use of you and your family. Selling it or distributing it commercially is not permitted."],
      },
      {
        h: "Changes",
        p: ["We may change these terms and the prices from time to time. The changed terms will be shown on this page."],
      },
    ],
  },

  refund: {
    title: "Refund Policy",
    description: "What happens if the Patrika does not arrive or is prepared incorrectly.",
    sections: [
      {
        h: "Look before you pay",
        p: ["A free preview and sample pages are available before payment, so you can decide after seeing them."],
      },
      {
        h: "Full refund",
        p: [
          "If, after payment, your Patrika cannot be prepared or does not reach you for a technical reason, the full amount is refunded.",
          "The refund is made to the same method used for payment.",
        ],
      },
      {
        h: "A mistake in the birth details",
        p: ["If you entered the wrong date, time or place of birth, contact us; the Patrika can be prepared again with the correct details."],
      },
      {
        h: "When there is no refund",
        p: ["The Patrika is a digital product. Once it has been prepared from correct details and delivered, a refund is not given solely for disagreement with the reading."],
      },
    ],
  },

  disclaimer: {
    title: "Disclaimer",
    description: "Astrology is guidance, not a guarantee.",
    sections: [
      {
        h: "Guidance, not a guarantee",
        p: [
          "The Janam Patrika, Panchang and other information here are for guidance and cultural purposes.",
          "Astrology shows tendencies and possibilities, not a fixed future. Your own decisions, effort and values shape life most of all.",
        ],
      },
      {
        h: "Not a substitute for professional advice",
        p: ["Take important decisions about health, law, money, education or marriage only with the advice of a qualified professional."],
      },
      {
        h: "Remedies are optional",
        p: ["The remedies in the Patrika are suggestions based on tradition and are entirely optional. We put no pressure on anyone to buy a puja, gemstone or any item."],
      },
      {
        h: "Calculation",
        p: ["Calculations use the Swiss Ephemeris and the Lahiri ayanamsa. A difference of even a few minutes in the birth time can change the Lagna and the divisional charts."],
      },
    ],
  },
};

export function legal(lang: Lang) {
  return lang === "hi" ? hi : en;
}
