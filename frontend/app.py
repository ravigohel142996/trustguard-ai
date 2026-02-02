import streamlit as st
import random
import time

# Page configuration
st.set_page_config(
    page_title="TrustGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Language translations
TRANSLATIONS = {
    "English": {
        "title": "TrustGuard AI – Scam & Fake Info Detector",
        "sidebar_title": "About TrustGuard AI",
        "sidebar_description": """
        **TrustGuard AI** is an advanced AI-powered system designed to protect you from:
        
        - 🚨 Scams and fraudulent messages
        - 📧 Phishing emails and links
        - 📱 Fake SMS and WhatsApp messages
        - 💰 Fraudulent investment offers
        - 🎯 Fake ads and promotions
        
        Simply paste any suspicious content and let our AI analyze it for you!
        """,
        "language_label": "Select Language",
        "input_label": "Enter message, link, email, or ad to analyze:",
        "input_placeholder": "Paste your suspicious message, link, email, or advertisement here...",
        "analyze_button": "🔍 Analyze",
        "analyzing": "Analyzing content...",
        "results_title": "Analysis Results",
        "trust_score_label": "Trust Score",
        "risk_level_label": "Risk Level",
        "explanation_label": "Detailed Explanation",
        "scam_category_label": "Detected Scam Category",
        "safe": "✅ Safe",
        "suspicious": "⚠️ Suspicious",
        "dangerous": "🚨 Dangerous",
        "clear_button": "Clear Results"
    },
    "Hindi": {
        "title": "TrustGuard AI – स्कैम और फर्जी जानकारी डिटेक्टर",
        "sidebar_title": "TrustGuard AI के बारे में",
        "sidebar_description": """
        **TrustGuard AI** एक उन्नत AI-संचालित प्रणाली है जो आपको निम्न से बचाती है:
        
        - 🚨 स्कैम और धोखाधड़ी संदेश
        - 📧 फिशिंग ईमेल और लिंक
        - 📱 नकली SMS और WhatsApp संदेश
        - 💰 नकली निवेश प्रस्ताव
        - 🎯 नकली विज्ञापन और प्रचार
        
        बस किसी भी संदिग्ध सामग्री को पेस्ट करें और हमारे AI को इसका विश्लेषण करने दें!
        """,
        "language_label": "भाषा चुनें",
        "input_label": "विश्लेषण के लिए संदेश, लिंक, ईमेल या विज्ञापन दर्ज करें:",
        "input_placeholder": "अपना संदिग्ध संदेश, लिंक, ईमेल या विज्ञापन यहाँ पेस्ट करें...",
        "analyze_button": "🔍 विश्लेषण करें",
        "analyzing": "सामग्री का विश्लेषण किया जा रहा है...",
        "results_title": "विश्लेषण परिणाम",
        "trust_score_label": "विश्वास स्कोर",
        "risk_level_label": "जोखिम स्तर",
        "explanation_label": "विस्तृत विवरण",
        "scam_category_label": "पहचाना गया स्कैम श्रेणी",
        "safe": "✅ सुरक्षित",
        "suspicious": "⚠️ संदिग्ध",
        "dangerous": "🚨 खतरनाक",
        "clear_button": "परिणाम साफ़ करें"
    }
}

# Scam categories for mock results
SCAM_CATEGORIES = {
    "English": [
        "No scam detected",
        "Phishing attempt",
        "Financial fraud",
        "Fake lottery/prize",
        "Investment scam",
        "Romance scam",
        "Tech support scam",
        "Impersonation fraud",
        "Fake job offer",
        "Cryptocurrency scam"
    ],
    "Hindi": [
        "कोई स्कैम नहीं मिला",
        "फिशिंग का प्रयास",
        "वित्तीय धोखाधड़ी",
        "नकली लॉटरी/पुरस्कार",
        "निवेश स्कैम",
        "रोमांस स्कैम",
        "तकनीकी सहायता स्कैम",
        "नकली पहचान धोखाधड़ी",
        "नकली नौकरी का प्रस्ताव",
        "क्रिप्टोकरेंसी स्कैम"
    ]
}

def get_mock_analysis(text, language):
    """Generate mock analysis results for testing"""
    # Simulate processing time
    time.sleep(2)
    
    # Generate random trust score
    trust_score = random.randint(0, 100)
    
    # Determine risk level based on trust score
    if trust_score >= 70:
        risk_level = TRANSLATIONS[language]["safe"]
        risk_color = "success"
        category_index = 0
    elif trust_score >= 40:
        risk_level = TRANSLATIONS[language]["suspicious"]
        risk_color = "warning"
        category_index = random.randint(1, 3)
    else:
        risk_level = TRANSLATIONS[language]["dangerous"]
        risk_color = "error"
        category_index = random.randint(4, 9)
    
    # Generate explanation
    if language == "English":
        if trust_score >= 70:
            explanation = f"The analyzed content appears to be legitimate. Our AI model found no significant red flags or suspicious patterns. Trust score: {trust_score}/100. However, always exercise caution with sensitive information."
        elif trust_score >= 40:
            explanation = f"The content shows some suspicious elements that warrant caution. Our AI detected potential warning signs including unusual language patterns or requests. Trust score: {trust_score}/100. Please verify the source before taking any action."
        else:
            explanation = f"⚠️ HIGH RISK DETECTED! The content exhibits multiple characteristics of a scam or fraudulent attempt. Trust score: {trust_score}/100. DO NOT share personal information, click links, or send money. Report this content immediately."
    else:
        if trust_score >= 70:
            explanation = f"विश्लेषण की गई सामग्री वैध प्रतीत होती है। हमारे AI मॉडल को कोई महत्वपूर्ण लाल झंडे या संदिग्ध पैटर्न नहीं मिले। विश्वास स्कोर: {trust_score}/100। हालांकि, संवेदनशील जानकारी के साथ हमेशा सावधानी बरतें।"
        elif trust_score >= 40:
            explanation = f"सामग्री में कुछ संदिग्ध तत्व हैं जो सावधानी की मांग करते हैं। हमारे AI ने असामान्य भाषा पैटर्न या अनुरोधों सहित संभावित चेतावनी संकेत पाए। विश्वास स्कोर: {trust_score}/100। कोई भी कार्रवाई करने से पहले कृपया स्रोत की पुष्टि करें।"
        else:
            explanation = f"⚠️ उच्च जोखिम का पता चला! सामग्री में स्कैम या धोखाधड़ी के कई लक्षण हैं। विश्वास स्कोर: {trust_score}/100। व्यक्तिगत जानकारी साझा न करें, लिंक पर क्लिक न करें, या पैसे न भेजें। इस सामग्री की तुरंत रिपोर्ट करें।"
    
    # Get scam category
    scam_category = SCAM_CATEGORIES[language][category_index]
    
    return {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "explanation": explanation,
        "scam_category": scam_category
    }

def main():
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/3d-fluency/94/security-shield-green.png", width=100)
        
        # Language selector
        language = st.selectbox(
            "🌐 Language / भाषा",
            ["English", "Hindi"],
            key="language_selector"
        )
        
        st.markdown("---")
        
        st.markdown(f"### {TRANSLATIONS[language]['sidebar_title']}")
        st.markdown(TRANSLATIONS[language]['sidebar_description'])
        
        st.markdown("---")
        st.markdown("**Version:** 1.0.0")
        st.markdown("**Status:** 🟢 Active")
    
    # Main content
    lang = st.session_state.get('language_selector', 'English')
    
    # Title
    st.title(TRANSLATIONS[lang]["title"])
    st.markdown("---")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_area(
            TRANSLATIONS[lang]["input_label"],
            placeholder=TRANSLATIONS[lang]["input_placeholder"],
            height=200,
            key="user_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button(
            TRANSLATIONS[lang]["analyze_button"],
            type="primary",
            use_container_width=True
        )
        
        if st.session_state.analysis_results:
            if st.button(TRANSLATIONS[lang]["clear_button"], use_container_width=True):
                st.session_state.analysis_results = None
                st.rerun()
    
    # Analysis
    if analyze_button and user_input.strip():
        with st.spinner(TRANSLATIONS[lang]["analyzing"]):
            results = get_mock_analysis(user_input, lang)
            st.session_state.analysis_results = results
    
    # Display results
    if st.session_state.analysis_results:
        st.markdown("---")
        st.markdown(f"## {TRANSLATIONS[lang]['results_title']}")
        
        results = st.session_state.analysis_results
        
        # Trust Score with Progress Bar
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {TRANSLATIONS[lang]['trust_score_label']}")
            st.progress(results['trust_score'] / 100)
            st.markdown(f"**{results['trust_score']}/100**")
        
        with col2:
            st.markdown(f"### {TRANSLATIONS[lang]['risk_level_label']}")
            if results['risk_color'] == 'success':
                st.success(results['risk_level'])
            elif results['risk_color'] == 'warning':
                st.warning(results['risk_level'])
            else:
                st.error(results['risk_level'])
        
        # Explanation
        st.markdown(f"### {TRANSLATIONS[lang]['explanation_label']}")
        st.info(results['explanation'])
        
        # Scam Category
        st.markdown(f"### {TRANSLATIONS[lang]['scam_category_label']}")
        st.markdown(f"**{results['scam_category']}**")
    
    elif analyze_button and not user_input.strip():
        st.warning("⚠️ Please enter some content to analyze!" if lang == "English" 
                   else "⚠️ कृपया विश्लेषण के लिए कुछ सामग्री दर्ज करें!")

if __name__ == "__main__":
    main()
