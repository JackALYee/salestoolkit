"""Page-wide language switching for the Sales Toolkit.

Why a runtime text-node sweep instead of `data-i18n` keys
--------------------------------------------------------
The toolkit page is assembled by concatenating raw HTML strings exported by a
dozen modules (`streamaxpedia_app.py`, `prospecting_flow.py`, … ~500 KB of
markup). Threading `data-i18n="key"` through all of it would touch every module,
every future edit, and would silently rot the moment someone adds a heading
without a key.

So instead: walk the DOM once, snapshot every text node and translatable
attribute, and swap them against a phrase dictionary keyed by the **English
text itself**. Modules stay untouched, new English copy keeps working (it just
stays English until a translation is added), and nothing can get out of sync.

The index is built lazily on the FIRST switch away from English, so the default
English load pays nothing. A debounced MutationObserver re-applies to content
the modules render with JS (search results, matrices, generated tables).

Coverage
--------
`PHRASES` covers the page chrome that every user sees — header, navigation,
section headings, the user guide, Marketing Resources, and common controls.
Deep reference content (the terminology database, long knowledge tables,
generated scripts) intentionally stays English: it is product/industry
vocabulary that sales staff use in English with customers anyway, and
machine-grade translation of it would do more harm than good. Add entries here
to widen coverage — nothing else needs changing.
"""
from __future__ import annotations

import json

# (code, native label, short chip label). English first = default.
LANGUAGES = [
    ("en", "English",    "EN"),
    ("zh", "中文",        "中文"),
    ("ja", "日本語",      "日本語"),
    ("es", "Español",    "ES"),
    ("pt", "Português",  "PT"),
    ("fr", "Français",   "FR"),
    ("it", "Italiano",   "IT"),
]

LANG_CODES = [c for c, _, _ in LANGUAGES]

# ── phrase dictionary ────────────────────────────────────────────────────────
# English source string -> {lang: translation}. Matched on the trimmed text of a
# text node or attribute, so keep keys byte-identical to what the modules emit.
PHRASES: dict[str, dict[str, str]] = {
    # --- header ------------------------------------------------------------
    "Global": {
        "zh": "全球", "ja": "グローバル", "es": "Global",
        "pt": "Global", "fr": "Mondiale", "it": "Globale"},
    "Trucking Division": {
        "zh": "货运产品线", "ja": "トラック事業部", "es": "División de Transporte",
        "pt": "Divisão de Transporte", "fr": "Division Poids Lourds",
        "it": "Divisione Autotrasporto"},
    "Streamax Sales Toolkit": {
        "zh": "锐明销售工具箱", "ja": "Streamax セールスツールキット",
        "es": "Kit de Ventas Streamax", "pt": "Kit de Vendas Streamax",
        "fr": "Boîte à Outils Commerciale Streamax",
        "it": "Toolkit Commerciale Streamax"},

    # --- navigation --------------------------------------------------------
    "Streamaxpedia": {
        "zh": "锐明百科", "ja": "Streamaxpedia", "es": "Streamaxpedia",
        "pt": "Streamaxpedia", "fr": "Streamaxpedia", "it": "Streamaxpedia"},
    "Prospecting Flow": {
        "zh": "客户开发流程", "ja": "見込み客開拓フロー", "es": "Flujo de Prospección",
        "pt": "Fluxo de Prospecção", "fr": "Parcours de Prospection",
        "it": "Flusso di Prospezione"},
    "Discovery Meeting": {
        "zh": "需求挖掘会议", "ja": "ディスカバリーミーティング",
        "es": "Reunión de Descubrimiento", "pt": "Reunião de Descoberta",
        "fr": "Réunion de Découverte", "it": "Incontro di Scoperta"},
    "Presentation": {
        "zh": "方案演示", "ja": "プレゼンテーション", "es": "Presentación",
        "pt": "Apresentação", "fr": "Présentation", "it": "Presentazione"},
    "Value Calculator": {
        "zh": "价值计算器", "ja": "バリュー計算ツール", "es": "Calculadora de Valor",
        "pt": "Calculadora de Valor", "fr": "Calculateur de Valeur",
        "it": "Calcolatore di Valore"},
    "Email Tool": {
        "zh": "邮件工具", "ja": "メールツール", "es": "Herramienta de Correo",
        "pt": "Ferramenta de E-mail", "fr": "Outil E-mail",
        "it": "Strumento Email"},
    "Marketing Resources": {
        "zh": "市场资源", "ja": "マーケティング資料",
        "es": "Recursos de Marketing", "pt": "Recursos de Marketing",
        "fr": "Ressources Marketing", "it": "Risorse di Marketing"},
    "Sales Configurator": {
        "zh": "销售配置器", "ja": "セールスコンフィギュレーター",
        "es": "Configurador de Ventas", "pt": "Configurador de Vendas",
        "fr": "Configurateur Commercial", "it": "Configuratore di Vendita"},

    # --- section headings --------------------------------------------------
    "Solution Validator": {
        "zh": "方案验证器", "ja": "ソリューション検証", "es": "Validador de Soluciones",
        "pt": "Validador de Soluções", "fr": "Validateur de Solution",
        "it": "Validatore di Soluzioni"},
    "Enterprise Sales Process": {
        "zh": "企业销售流程", "ja": "エンタープライズ営業プロセス",
        "es": "Proceso de Venta Empresarial", "pt": "Processo de Vendas Empresarial",
        "fr": "Processus de Vente Entreprise", "it": "Processo di Vendita Enterprise"},
    "Discovery Meetings": {
        "zh": "需求挖掘会议", "ja": "ディスカバリーミーティング",
        "es": "Reuniones de Descubrimiento", "pt": "Reuniões de Descoberta",
        "fr": "Réunions de Découverte", "it": "Incontri di Scoperta"},
    "Streamax Closed-Loop Trucking Solution": {
        "zh": "锐明货运闭环解决方案", "ja": "Streamax クローズドループ輸送ソリューション",
        "es": "Solución de Transporte de Ciclo Cerrado Streamax",
        "pt": "Solução de Transporte em Ciclo Fechado Streamax",
        "fr": "Solution Poids Lourds en Boucle Fermée Streamax",
        "it": "Soluzione Autotrasporto a Ciclo Chiuso Streamax"},
    "Fleet Parameters": {
        "zh": "车队参数", "ja": "車両パラメータ", "es": "Parámetros de Flota",
        "pt": "Parâmetros da Frota", "fr": "Paramètres de Flotte",
        "it": "Parametri della Flotta"},
    "Estimated Annual Savings": {
        "zh": "预计年度节省", "ja": "年間削減額（推定）",
        "es": "Ahorro Anual Estimado", "pt": "Economia Anual Estimada",
        "fr": "Économies Annuelles Estimées", "it": "Risparmio Annuo Stimato"},
    "Value Proposition & Justification": {
        "zh": "价值主张与论证", "ja": "価値提案と根拠",
        "es": "Propuesta de Valor y Justificación",
        "pt": "Proposta de Valor e Justificação",
        "fr": "Proposition de Valeur et Justification",
        "it": "Proposta di Valore e Giustificazione"},
    "Route Data": {
        "zh": "路线数据", "ja": "ルートデータ", "es": "Datos de Ruta",
        "pt": "Dados da Rota", "fr": "Données d'Itinéraire", "it": "Dati di Percorso"},
    "Reconciliation": {
        "zh": "对账", "ja": "照合", "es": "Conciliación",
        "pt": "Reconciliação", "fr": "Rapprochement", "it": "Riconciliazione"},
    "Cost Parameters": {
        "zh": "成本参数", "ja": "コストパラメータ", "es": "Parámetros de Costo",
        "pt": "Parâmetros de Custo", "fr": "Paramètres de Coût",
        "it": "Parametri di Costo"},
    "Revenue Parameters": {
        "zh": "收入参数", "ja": "収益パラメータ", "es": "Parámetros de Ingresos",
        "pt": "Parâmetros de Receita", "fr": "Paramètres de Revenus",
        "it": "Parametri di Ricavo"},
    "Streamax Sales Configurator": {
        "zh": "锐明销售配置器", "ja": "Streamax セールスコンフィギュレーター",
        "es": "Configurador de Ventas Streamax", "pt": "Configurador de Vendas Streamax",
        "fr": "Configurateur Commercial Streamax",
        "it": "Configuratore di Vendita Streamax"},
    "Streamax Drip Mailer": {
        "zh": "锐明邮件触达", "ja": "Streamax ドリップメーラー",
        "es": "Streamax Drip Mailer", "pt": "Streamax Drip Mailer",
        "fr": "Streamax Drip Mailer", "it": "Streamax Drip Mailer"},
    "Component Library": {
        "zh": "组件库", "ja": "コンポーネントライブラリ", "es": "Biblioteca de Componentes",
        "pt": "Biblioteca de Componentes", "fr": "Bibliothèque de Composants",
        "it": "Libreria Componenti"},
    "Composition Discovery": {
        "zh": "组合探索", "ja": "構成ディスカバリー", "es": "Descubrimiento de Composición",
        "pt": "Descoberta de Composição", "fr": "Découverte de Composition",
        "it": "Scoperta della Composizione"},
    "Streamax Ecosystem Map": {
        "zh": "锐明生态图谱", "ja": "Streamax エコシステムマップ",
        "es": "Mapa del Ecosistema Streamax", "pt": "Mapa do Ecossistema Streamax",
        "fr": "Carte de l'Écosystème Streamax", "it": "Mappa dell'Ecosistema Streamax"},
    "How to Use It": {
        "zh": "使用方法", "ja": "使い方", "es": "Cómo Usarlo",
        "pt": "Como Usar", "fr": "Mode d'Emploi", "it": "Come Usarlo"},

    # --- common controls ---------------------------------------------------
    "Copy": {
        "zh": "复制", "ja": "コピー", "es": "Copiar",
        "pt": "Copiar", "fr": "Copier", "it": "Copia"},
    "Copy prompt": {
        "zh": "复制提示词", "ja": "プロンプトをコピー", "es": "Copiar indicación",
        "pt": "Copiar prompt", "fr": "Copier l'invite", "it": "Copia prompt"},
    "Copied to Clipboard!": {
        "zh": "已复制到剪贴板！", "ja": "クリップボードにコピーしました！",
        "es": "¡Copiado al portapapeles!", "pt": "Copiado para a área de transferência!",
        "fr": "Copié dans le presse-papiers !", "it": "Copiato negli appunti!"},
    "Open Jerry GPT": {
        "zh": "打开 Jerry GPT", "ja": "Jerry GPT を開く", "es": "Abrir Jerry GPT",
        "pt": "Abrir Jerry GPT", "fr": "Ouvrir Jerry GPT", "it": "Apri Jerry GPT"},
    "Go to Section": {
        "zh": "前往该板块", "ja": "セクションへ移動", "es": "Ir a la sección",
        "pt": "Ir para a seção", "fr": "Aller à la section", "it": "Vai alla sezione"},
    "TSP / Channel Partner": {
        "zh": "TSP / 渠道伙伴", "ja": "TSP / チャネルパートナー",
        "es": "TSP / Socio de Canal", "pt": "TSP / Parceiro de Canal",
        "fr": "TSP / Partenaire Canal", "it": "TSP / Partner di Canale"},
    "End Users (Fleets)": {
        "zh": "终端用户（车队）", "ja": "エンドユーザー（フリート）",
        "es": "Usuarios Finales (Flotas)", "pt": "Usuários Finais (Frotas)",
        "fr": "Utilisateurs Finaux (Flottes)", "it": "Utenti Finali (Flotte)"},
    "Email Template": {
        "zh": "邮件模板", "ja": "メールテンプレート", "es": "Plantilla de Correo",
        "pt": "Modelo de E-mail", "fr": "Modèle d'E-mail", "it": "Modello Email"},
    "Cold Calling Script": {
        "zh": "陌生电话话术", "ja": "コールドコール台本",
        "es": "Guion de Llamada en Frío", "pt": "Roteiro de Ligação Fria",
        "fr": "Script d'Appel à Froid", "it": "Script di Chiamata a Freddo"},
    "Elevator Pitch Script": {
        "zh": "电梯演讲话术", "ja": "エレベーターピッチ台本",
        "es": "Guion de Presentación Breve", "pt": "Roteiro de Pitch Rápido",
        "fr": "Script de Pitch Éclair", "it": "Script di Presentazione Breve"},
    "Tour Streamaxpedia": {
        "zh": "浏览锐明百科", "ja": "Streamaxpedia を見る",
        "es": "Recorrer Streamaxpedia", "pt": "Explorar Streamaxpedia",
        "fr": "Découvrir Streamaxpedia", "it": "Esplora Streamaxpedia"},
    "Meet Jerry GPT": {
        "zh": "认识 Jerry GPT", "ja": "Jerry GPT を知る",
        "es": "Conoce a Jerry GPT", "pt": "Conheça o Jerry GPT",
        "fr": "Rencontrer Jerry GPT", "it": "Scopri Jerry GPT"},
    "Language": {
        "zh": "语言", "ja": "言語", "es": "Idioma",
        "pt": "Idioma", "fr": "Langue", "it": "Lingua"},

    # --- user guide --------------------------------------------------------
    "Streamax Sales Toolkit User Guide": {
        "zh": "锐明销售工具箱使用指南", "ja": "Streamax セールスツールキット利用ガイド",
        "es": "Guía de Uso del Kit de Ventas Streamax",
        "pt": "Guia de Uso do Kit de Vendas Streamax",
        "fr": "Guide d'Utilisation de la Boîte à Outils Commerciale Streamax",
        "it": "Guida all'Uso del Toolkit Commerciale Streamax"},
    "A digital Swiss Army knife for Streamax sales. Every tool you need across the sales cycle — product knowledge, scripts, discovery questions, ROI maths, outreach and configuration — in one place. Eight sections, each usable on its own.": {
        "zh": "专为锐明销售打造的“数字瑞士军刀”。销售全周期所需的一切——产品知识、话术、挖掘问题、ROI 测算、客户触达与选型配置——集中在一个平台。八大板块，各自独立可用。",
        "ja": "Streamax 営業のための「デジタル・スイスアーミーナイフ」。製品知識、トークスクリプト、ヒアリング質問、ROI 計算、アプローチ、構成設計まで、営業サイクル全体に必要なツールを一つに集約。8 つのセクションはそれぞれ単独でも使えます。",
        "es": "Una navaja suiza digital para la fuerza de ventas de Streamax. Todo lo necesario en el ciclo comercial —conocimiento de producto, guiones, preguntas de descubrimiento, cálculo de ROI, prospección y configuración— en un solo lugar. Ocho secciones, cada una utilizable por separado.",
        "pt": "Um canivete suíço digital para as vendas da Streamax. Tudo o que você precisa no ciclo comercial — conhecimento de produto, roteiros, perguntas de descoberta, cálculo de ROI, prospecção e configuração — num só lugar. Oito seções, cada uma utilizável isoladamente.",
        "fr": "Un couteau suisse numérique pour les commerciaux Streamax. Tout ce dont vous avez besoin sur le cycle de vente — connaissance produit, scripts, questions de découverte, calcul du ROI, prospection et configuration — au même endroit. Huit sections, chacune utilisable seule.",
        "it": "Un coltellino svizzero digitale per la forza vendita Streamax. Tutto ciò che serve nel ciclo di vendita — conoscenza di prodotto, script, domande di scoperta, calcolo del ROI, prospezione e configurazione — in un unico posto. Otto sezioni, ciascuna utilizzabile singolarmente."},
    "Product knowledge base with a search mode, a hardware Product Matrix with a validator that catches invalid architectures, the interactive Ecosystem Map, and Jerry GPT.": {
        "zh": "产品知识库：搜索模式、带方案验证器的硬件产品矩阵（可识别无效架构）、交互式生态图谱，以及 Jerry GPT。",
        "ja": "製品ナレッジベース：検索モード、無効な構成を検出するバリデーター付き製品マトリクス、インタラクティブなエコシステムマップ、そして Jerry GPT。",
        "es": "Base de conocimiento de producto con modo de búsqueda, Matriz de Producto con validador que detecta arquitecturas inválidas, Mapa del Ecosistema interactivo y Jerry GPT.",
        "pt": "Base de conhecimento de produto com modo de busca, Matriz de Produto com validador que detecta arquiteturas inválidas, Mapa do Ecossistema interativo e Jerry GPT.",
        "fr": "Base de connaissances produit avec mode recherche, Matrice Produit dotée d'un validateur détectant les architectures invalides, Carte de l'Écosystème interactive et Jerry GPT.",
        "it": "Base di conoscenza di prodotto con modalità ricerca, Matrice Prodotto con validatore che rileva architetture non valide, Mappa dell'Ecosistema interattiva e Jerry GPT."},
    "The 7-step enterprise sales process plus a script library — email templates, cold-call scripts and elevator pitches, split by TSP partner vs. end-user fleet.": {
        "zh": "7 步企业销售流程，外加话术库——邮件模板、陌拜电话话术、电梯演讲，按 TSP 渠道伙伴与终端车队分开编写。",
        "ja": "7 ステップのエンタープライズ営業プロセスとスクリプト集——メールテンプレート、コールドコール台本、エレベーターピッチを TSP パートナー向けとエンドユーザー車両向けに分けて収録。",
        "es": "El proceso de venta empresarial de 7 pasos más una biblioteca de guiones: plantillas de correo, llamadas en frío y presentaciones breves, separadas para socios TSP y flotas de usuario final.",
        "pt": "O processo de vendas empresarial em 7 etapas mais uma biblioteca de roteiros: modelos de e-mail, ligações frias e pitches rápidos, separados para parceiros TSP e frotas de usuário final.",
        "fr": "Le processus de vente entreprise en 7 étapes et une bibliothèque de scripts : modèles d'e-mail, appels à froid et pitchs éclair, distincts pour partenaires TSP et flottes utilisateurs.",
        "it": "Il processo di vendita enterprise in 7 fasi più una libreria di script: modelli email, chiamate a freddo e presentazioni brevi, distinti per partner TSP e flotte utente finale."},
    "A structured question bank that walks you from business model to pain points, deployment constraints and budget — separate tracks for TSPs and end users.": {
        "zh": "结构化问题库，从商业模式一路问到痛点、部署限制与预算——TSP 与终端用户分设两套路径。",
        "ja": "ビジネスモデルから課題、導入制約、予算までを順に引き出す構造化された質問集。TSP 向けとエンドユーザー向けの 2 系統。",
        "es": "Un banco de preguntas estructurado que va del modelo de negocio a los puntos de dolor, las restricciones de despliegue y el presupuesto, con rutas separadas para TSP y usuarios finales.",
        "pt": "Um banco de perguntas estruturado que vai do modelo de negócio às dores, restrições de implantação e orçamento, com trilhas separadas para TSPs e usuários finais.",
        "fr": "Une banque de questions structurée qui va du modèle économique aux points de douleur, contraintes de déploiement et budget, avec des parcours distincts pour TSP et utilisateurs finaux.",
        "it": "Un banco di domande strutturato che va dal modello di business ai punti critici, vincoli di installazione e budget, con percorsi separati per TSP e utenti finali."},
    "The customer-facing story: animated risk visualisations and the Closed-Loop Journey across 10 touchpoints, each with a matching speaker script.": {
        "zh": "面向客户的叙事：动态风险可视化与覆盖 10 个关键触点的闭环旅程，每个触点均配讲解话术。",
        "ja": "顧客向けストーリー：リスクを可視化するアニメーションと、10 の接点を貫くクローズドループ・ジャーニー。各接点に対応するトークスクリプト付き。",
        "es": "La narrativa para el cliente: visualizaciones animadas de riesgo y el Recorrido de Ciclo Cerrado en 10 puntos de contacto, cada uno con su guion de presentación.",
        "pt": "A narrativa para o cliente: visualizações animadas de risco e a Jornada em Ciclo Fechado em 10 pontos de contato, cada um com seu roteiro de apresentação.",
        "fr": "Le récit client : visualisations animées des risques et le Parcours en Boucle Fermée sur 10 points de contact, chacun avec son script de présentation.",
        "it": "La narrazione per il cliente: visualizzazioni animate del rischio e il Percorso a Ciclo Chiuso su 10 punti di contatto, ciascuno con il relativo script."},
    "Prove the money. TCO savings from fuel, claims and insurance; an IFTA optimiser for North American routes; and an internal margin and payback calculator.": {
        "zh": "用数据证明收益。测算燃油、事故理赔与保险带来的 TCO 节省；面向北美线路的 IFTA 优化器；以及内部毛利与回本周期计算器。",
        "ja": "金額で証明する。燃料・事故賠償・保険による TCO 削減、北米ルート向け IFTA 最適化ツール、社内向けの粗利・回収期間計算ツール。",
        "es": "Demuestre el dinero. Ahorro de TCO en combustible, siniestros y seguros; un optimizador IFTA para rutas norteamericanas; y una calculadora interna de margen y recuperación.",
        "pt": "Prove o dinheiro. Economia de TCO em combustível, sinistros e seguros; um otimizador IFTA para rotas norte-americanas; e uma calculadora interna de margem e payback.",
        "fr": "Prouvez le gain. Économies de TCO sur carburant, sinistres et assurance ; un optimiseur IFTA pour les itinéraires nord-américains ; et un calculateur interne de marge et de retour sur investissement.",
        "it": "Dimostra il ritorno. Risparmi di TCO su carburante, sinistri e assicurazione; un ottimizzatore IFTA per le rotte nordamericane; e un calcolatore interno di margine e payback."},
    "Build a signature, compose with {first_name} / {company} variables, upload a CSV and send on a human-looking schedule with full logs.": {
        "zh": "生成签名档，使用 {first_name} / {company} 变量撰写内容，上传 CSV 名单，按拟人化节奏发送并保留完整日志。",
        "ja": "署名を作成し、{first_name} / {company} 変数で本文を作成。CSV をアップロードして人間らしい間隔で送信し、ログをすべて記録します。",
        "es": "Cree una firma, redacte con variables {first_name} / {company}, suba un CSV y envíe con un ritmo natural y registro completo.",
        "pt": "Crie uma assinatura, redija com variáveis {first_name} / {company}, envie um CSV e dispare num ritmo natural com registro completo.",
        "fr": "Créez une signature, rédigez avec les variables {first_name} / {company}, importez un CSV et envoyez à un rythme naturel avec journalisation complète.",
        "it": "Crea una firma, componi con le variabili {first_name} / {company}, carica un CSV e invia con un ritmo naturale e log completi."},
    "Customer-ready collateral: the Sentinel product site to send to prospects, and the product decks you can download and forward.": {
        "zh": "可直接面向客户的物料：可发送给潜在客户的 Sentinel 产品官网，以及可下载转发的产品资料。",
        "ja": "顧客にそのまま渡せる資料：見込み客に送れる Sentinel 製品サイトと、ダウンロードして転送できる製品資料。",
        "es": "Material listo para el cliente: el sitio del producto Sentinel para enviar a prospectos y las presentaciones descargables para reenviar.",
        "pt": "Material pronto para o cliente: o site do produto Sentinel para enviar a prospects e as apresentações para baixar e encaminhar.",
        "fr": "Supports prêts à envoyer : le site produit Sentinel à transmettre aux prospects et les présentations téléchargeables à faire suivre.",
        "it": "Materiali pronti per il cliente: il sito del prodotto Sentinel da inviare ai potenziali clienti e le presentazioni scaricabili da inoltrare."},
    "A guided BOM builder for the North America sales list. It applies the camera, interface and cable rules for you and exports the approved Excel material list.": {
        "zh": "面向北美销售清单的引导式选配工具。自动套用摄像头、接口与线缆规则，并导出符合规范的 Excel 物料清单。",
        "ja": "北米セールスリスト向けのガイド付き BOM 作成ツール。カメラ・インターフェース・ケーブルのルールを自動適用し、承認済みフォーマットの Excel 部材表を出力します。",
        "es": "Un generador guiado de lista de materiales para el catálogo de Norteamérica. Aplica las reglas de cámaras, interfaces y cables y exporta el Excel aprobado.",
        "pt": "Um gerador guiado de lista de materiais para o catálogo da América do Norte. Aplica as regras de câmeras, interfaces e cabos e exporta o Excel aprovado.",
        "fr": "Un générateur guidé de nomenclature pour le catalogue Amérique du Nord. Il applique les règles caméras, interfaces et câbles et exporte le fichier Excel approuvé.",
        "it": "Un generatore guidato di distinta base per il listino Nord America. Applica le regole di telecamere, interfacce e cavi ed esporta l'Excel approvato."},
    "Tip: use the language selector at the top right to switch the interface. Product names, part numbers and technical vocabulary stay in English on purpose — that is how customers and the factory refer to them.": {
        "zh": "提示：右上角的语言选择器可切换界面语言。产品名称、料号与技术术语有意保留英文——客户与工厂都以英文称呼它们。",
        "ja": "ヒント：右上の言語セレクターで表示言語を切り替えられます。製品名・型番・技術用語は意図的に英語のままです——顧客も工場も英語で呼ぶためです。",
        "es": "Consejo: use el selector de idioma arriba a la derecha para cambiar la interfaz. Los nombres de producto, números de pieza y vocabulario técnico permanecen en inglés a propósito: así los nombran los clientes y la fábrica.",
        "pt": "Dica: use o seletor de idioma no canto superior direito para mudar a interface. Nomes de produto, códigos de peça e vocabulário técnico permanecem em inglês de propósito — é assim que clientes e fábrica os chamam.",
        "fr": "Astuce : utilisez le sélecteur de langue en haut à droite pour changer l'interface. Les noms de produits, références et termes techniques restent volontairement en anglais — c'est ainsi que les clients et l'usine les désignent.",
        "it": "Suggerimento: usa il selettore di lingua in alto a destra per cambiare l'interfaccia. Nomi di prodotto, codici articolo e terminologia tecnica restano in inglese di proposito: è così che li chiamano clienti e fabbrica."},

    # --- marketing resources ------------------------------------------------
    "Marketing Materials": {
        "zh": "市场物料", "ja": "マーケティング資料",
        "es": "Materiales de Marketing", "pt": "Materiais de Marketing",
        "fr": "Supports Marketing", "it": "Materiali di Marketing"},
    "Customer-facing material you can send as-is. Everything here is cleared for external sharing.": {
        "zh": "可直接发送给客户的物料。此处内容均已批准对外分享。",
        "ja": "そのまま顧客に送れる資料です。ここにあるものはすべて社外共有が承認されています。",
        "es": "Material para el cliente que puede enviar tal cual. Todo lo de aquí está aprobado para compartir externamente.",
        "pt": "Material para o cliente que você pode enviar como está. Tudo aqui está aprovado para compartilhamento externo.",
        "fr": "Supports destinés aux clients, à envoyer tels quels. Tout ici est validé pour un partage externe.",
        "it": "Materiale per il cliente da inviare così com'è. Tutto qui è approvato per la condivisione esterna."},
    "Product Websites": {
        "zh": "产品官网", "ja": "製品サイト", "es": "Sitios de Producto",
        "pt": "Sites de Produto", "fr": "Sites Produit", "it": "Siti di Prodotto"},
    "Downloadable Decks": {
        "zh": "可下载资料", "ja": "ダウンロード資料",
        "es": "Presentaciones Descargables", "pt": "Apresentações para Download",
        "fr": "Présentations à Télécharger", "it": "Presentazioni Scaricabili"},
    "Open site": {
        "zh": "打开网站", "ja": "サイトを開く", "es": "Abrir sitio",
        "pt": "Abrir site", "fr": "Ouvrir le site", "it": "Apri il sito"},
    "Download": {
        "zh": "下载", "ja": "ダウンロード", "es": "Descargar",
        "pt": "Baixar", "fr": "Télécharger", "it": "Scarica"},
    "Public — safe to send to customers": {
        "zh": "公开——可安全发送给客户",
        "ja": "公開——顧客に送付可能",
        "es": "Público — seguro para enviar a clientes",
        "pt": "Público — seguro para enviar a clientes",
        "fr": "Public — peut être envoyé aux clients",
        "it": "Pubblico — sicuro da inviare ai clienti"},
    "Partner enablement — check before forwarding externally": {
        "zh": "伙伴赋能材料——对外转发前请先确认",
        "ja": "パートナー向け資料——社外転送前に確認してください",
        "es": "Habilitación de socios — verifique antes de reenviar externamente",
        "pt": "Capacitação de parceiros — verifique antes de encaminhar externamente",
        "fr": "Activation partenaires — à vérifier avant tout envoi externe",
        "it": "Abilitazione partner — verificare prima di inoltrare all'esterno"},
}


def switcher_html() -> str:
    """The fixed top-right language selector."""
    opts = "".join(
        f'<button type="button" class="stmx-lang-opt" data-lang="{code}" '
        f'onclick="stmxSetLang(\'{code}\')">{native}</button>'
        for code, native, _ in LANGUAGES
    )
    return f"""
    <div class="stmx-lang" id="stmx-lang">
      <button type="button" class="stmx-lang-btn" onclick="stmxToggleLangMenu(event)"
              aria-haspopup="true" aria-expanded="false" title="Language">
        <i data-lucide="languages"></i>
        <span id="stmx-lang-current">EN</span>
        <i data-lucide="chevron-down" class="stmx-lang-caret"></i>
      </button>
      <div class="stmx-lang-menu" id="stmx-lang-menu">{opts}</div>
    </div>
    """


def switcher_css() -> str:
    return """
    /* Shares the top-right corner with the existing user pill. The cluster
       owns the fixed placement so neither can overlap the other, whatever the
       signed-in email's width. */
    .stmx-topright{position:fixed;top:18px;right:18px;z-index:1000;
      display:flex;align-items:center;gap:10px}
    .stmx-topright .user-pill{position:static;top:auto;right:auto;z-index:auto}
    .stmx-lang{position:relative;font-family:inherit}
    .stmx-lang-btn{display:flex;align-items:center;gap:7px;padding:7px 12px;border-radius:999px;
      background:rgba(10,15,25,.82);border:1px solid rgba(255,255,255,.16);color:#E6EAF0;
      font-size:.78rem;font-weight:600;cursor:pointer;backdrop-filter:blur(10px);transition:.2s}
    .stmx-lang-btn:hover{border-color:var(--primary-green,#2AF598);color:var(--primary-green,#2AF598)}
    .stmx-lang-btn i{width:14px;height:14px}
    .stmx-lang-caret{transition:transform .2s}
    .stmx-lang.open .stmx-lang-caret{transform:rotate(180deg)}
    .stmx-lang-menu{display:none;position:absolute;top:calc(100% + 6px);right:0;min-width:150px;
      background:rgba(8,12,20,.97);border:1px solid rgba(255,255,255,.14);border-radius:12px;
      padding:6px;backdrop-filter:blur(14px);box-shadow:0 12px 32px rgba(0,0,0,.5)}
    .stmx-lang.open .stmx-lang-menu{display:block}
    .stmx-lang-opt{display:block;width:100%;text-align:left;padding:8px 12px;border:none;
      background:transparent;color:#A0AEC0;font-size:.82rem;font-family:inherit;border-radius:8px;
      cursor:pointer;transition:.15s}
    .stmx-lang-opt:hover{background:rgba(255,255,255,.07);color:#E6EAF0}
    .stmx-lang-opt.active{background:rgba(42,245,152,.14);color:var(--primary-green,#2AF598);font-weight:700}
    @media (max-width:640px){
      .stmx-topright{top:10px;right:10px;gap:6px}
      .stmx-lang-btn{padding:5px 9px;font-size:.7rem}
      .stmx-lang-menu{min-width:132px}}
    """


def engine_js() -> str:
    """Text-node sweep translator. See module docstring for why."""
    return """
    <script>
    (function () {
      var PHRASES = __PHRASES__;
      var LABELS  = __LABELS__;
      var ATTRS   = ['placeholder', 'title', 'aria-label', 'alt'];
      var SKIP    = {SCRIPT:1, STYLE:1, NOSCRIPT:1, CODE:1, PRE:1, TEXTAREA:1};

      var lang = 'en';
      var nodes = null;   // [{n:textNode, o:originalText}]
      var attrs = null;   // [{e:element, a:attrName, o:originalValue}]
      var seenN = null;   // WeakSet of already-indexed text nodes
      var seenA = null;   // WeakSet of already-indexed elements
      var applying = false;

      function insideSkip(el) {
        for (var p = el; p; p = p.parentElement) {
          if (SKIP[p.tagName]) return true;
          if (p.classList && p.classList.contains('stmx-no-i18n')) return true;
        }
        return false;
      }

      // Built lazily on the first switch: English readers never pay for this.
      //
      // INCREMENTAL, and that is load-bearing. Re-indexing wholesale would
      // re-snapshot text this engine had already translated and treat it as the
      // English original — after one observer tick the page would be frozen in
      // whatever language it was in, and "back to English" would restore the
      // translation. Each node's original is captured exactly once, ever.
      function index() {
        if (!nodes) { nodes = []; attrs = []; seenN = new WeakSet(); seenA = new WeakSet(); }
        var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
        var n;
        while ((n = w.nextNode())) {
          if (!n.nodeValue || !n.nodeValue.trim()) continue;
          if (seenN.has(n)) continue;
          if (insideSkip(n.parentElement)) continue;
          seenN.add(n);
          nodes.push({n: n, o: n.nodeValue});
        }
        var all = document.body.querySelectorAll('*');
        for (var i = 0; i < all.length; i++) {
          if (seenA.has(all[i])) continue;
          seenA.add(all[i]);
          for (var j = 0; j < ATTRS.length; j++) {
            var v = all[i].getAttribute(ATTRS[j]);
            if (v && v.trim()) attrs.push({e: all[i], a: ATTRS[j], o: v});
          }
        }
      }

      function tr(text, code) {
        var hit = PHRASES[text.trim()];
        return (hit && hit[code]) ? hit[code] : null;
      }

      function apply(code) {
        applying = true;
        index();
        for (var i = 0; i < nodes.length; i++) {
          var rec = nodes[i];
          if (!rec.n.parentNode) continue;              // detached since indexing
          if (code === 'en') { rec.n.nodeValue = rec.o; continue; }
          var t = tr(rec.o, code);
          if (t === null) { rec.n.nodeValue = rec.o; continue; }
          // Preserve the original leading/trailing whitespace so inline layout
          // (e.g. "<i></i> Streamaxpedia") doesn't collapse.
          var lead = rec.o.match(/^\\s*/)[0], tail = rec.o.match(/\\s*$/)[0];
          rec.n.nodeValue = lead + t + tail;
        }
        for (var k = 0; k < attrs.length; k++) {
          var a = attrs[k];
          if (!a.e.isConnected) continue;
          var av = (code === 'en') ? a.o : (tr(a.o, code) || a.o);
          if (a.e.getAttribute(a.a) !== av) a.e.setAttribute(a.a, av);
        }
        document.documentElement.setAttribute('lang', code);
        // Let our own writes settle before the observer listens again.
        setTimeout(function () { applying = false; }, 0);
      }

      var pending = null;
      function reindexSoon() {
        if (lang === 'en' || applying) return;   // nothing to do / our own write
        clearTimeout(pending);
        pending = setTimeout(function () { apply(lang); }, 260);
      }

      window.stmxSetLang = function (code) {
        lang = code;
        try { localStorage.setItem('stmx_lang', code); } catch (e) {}
        apply(code);
        var cur = document.getElementById('stmx-lang-current');
        if (cur) cur.textContent = LABELS[code] || code.toUpperCase();
        var opts = document.querySelectorAll('.stmx-lang-opt');
        for (var i = 0; i < opts.length; i++)
          opts[i].classList.toggle('active', opts[i].getAttribute('data-lang') === code);
        var box = document.getElementById('stmx-lang');
        if (box) box.classList.remove('open');
      };

      window.stmxToggleLangMenu = function (ev) {
        ev.stopPropagation();
        var box = document.getElementById('stmx-lang');
        if (box) box.classList.toggle('open');
      };
      document.addEventListener('click', function () {
        var box = document.getElementById('stmx-lang');
        if (box) box.classList.remove('open');
      });

      function boot() {
        var saved = 'en';
        try { saved = localStorage.getItem('stmx_lang') || 'en'; } catch (e) {}
        if (LABELS[saved] && saved !== 'en') window.stmxSetLang(saved);
        else window.stmxSetLang('en');
        // Modules render content with JS (search hits, matrices, tables) —
        // re-apply after the DOM settles.
        new MutationObserver(reindexSoon)
          .observe(document.body, {childList: true, subtree: true});
      }
      if (document.readyState === 'loading')
        document.addEventListener('DOMContentLoaded', boot);
      else boot();
    })();
    </script>
    """.replace("__PHRASES__", json.dumps(PHRASES, ensure_ascii=False)) \
       .replace("__LABELS__", json.dumps({c: s for c, _, s in LANGUAGES}, ensure_ascii=False))
