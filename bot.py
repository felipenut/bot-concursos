import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler

# Configuração de logs para ver erros no console
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 1. Definição dos Estados da Conversa
(ESCOLHER_CARREIRA, ESCOLHER_CONCURSO, ESCOLHER_MATERIA, 
 ESCOLHER_QUANTIDADE, ESCOLHER_TEMPO) = range(5)

# 2. Banco de Dados de Editais (Baseado nos arquivos enviados)
DADOS_CONCURSOS = {
    "PM": {
        "PMBA 2025": [
            "Todas", "Língua Portuguesa", "História do Brasil", "Geografia do Brasil", 
            "Atualidades", "Informática", "Direito Constitucional", "Direitos Humanos", 
            "Direito Administrativo", "Direito Penal", "Direito Processual Penal", 
            "Direito Penal Militar", "Legislação Extravagante"
        ],
        "PMAL 2026": [
            "Todas", "Língua Portuguesa", "Matemática", "Informática", 
            "Inglês", "Atualidades", "História de Alagoas", "Geografia de Alagoas", 
            "Direito Constitucional", "Direito Administrativo", "Direito Penal", 
            "Direito Processual Penal", "Direitos Humanos", "Legislação da PMAL"
        ],
        "PMRR 2018": ["Todas", "Português", "Raciocínio Lógico", "Atualidades", "Noções de Direito"]
    },
    "PC": {
        "PCBA 2022": [
            "Todas", "Língua Portuguesa", "Raciocínio Lógico", "Informática", 
            "Direito Civil", "Direito Administrativo", "Direito Constitucional", 
            "Direito Penal", "Direito Processual Penal", "Legislação Extravagante"
        ],
        "PCMA (Delegado)": [
            "Todas", "Direito Civil", "Direito Processual Civil", "Direito Penal", 
            "Direito Constitucional", "Direito Administrativo", "Direito Ambiental"
        ]
    },
    "GCM": {
        "GCM Salvador 2019": [
            "Todas", "Língua Portuguesa", "Raciocínio Lógico", "Informática", 
            "Legislação Específica", "Noções de Direito"
        ]
    },
    "PF": {
        "PF 2025": [
            "Todas", "Português", "Direito Administrativo", "Direito Constitucional", 
            "Direito Penal", "Direito Processual Penal", "Informática", "Raciocínio Lógico",
            "Estatística", "Contabilidade"
        ]
    },
    "PRF": {
        "PRF 2021": [
            "Todas", "Língua Portuguesa", "Raciocínio Lógico-Matemático", "Informática", 
            "Física", "Ética", "Geopolítica", "Inglês", "Espanhol", 
            "Legislação de Trânsito", "Direito Administrativo", "Direito Constitucional"
        ]
    },
    "POLICIAL PENAL": {
        "SEJUSP MG 2025": [
            "Todas", "Língua Portuguesa", "Raciocínio Lógico", "Informática", 
            "Direito Constitucional", "Direito Penal", "Direitos Humanos"
        ],
        "AGEPEN PB 2008": ["Todas", "Português", "Atualidades", "Noções de Direito"]
    }
}

# --- FUNÇÕES DE FLUXO ---

async def iniciar_treino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Passo 1: Pergunta a carreira."""
    keyboard = [[InlineKeyboardButton(k, callback_data=k)] for k in DADOS_CONCURSOS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("📚 **MODO TREINO ATIVADO**\n\nEscolha uma carreira para começar:", 
                                   reply_markup=reply_markup, parse_mode="Markdown")
    return ESCOLHER_CARREIRA

async def escolher_concurso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Passo 2: Pergunta o concurso específico."""
    query = update.callback_query
    await query.answer()
    context.user_data['carreira'] = query.data
    
    concursos = DADOS_CONCURSOS[query.data]
    keyboard = [[InlineKeyboardButton(c, callback_data=c)] for c in concursos.keys()]
    
    await query.edit_message_text(text=f"Ótimo! Agora escolha o edital da {query.data}:", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return ESCOLHER_CONCURSO

async def escolher_materia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Passo 3: Pergunta a matéria."""
    query = update.callback_query
    await query.answer()
    context.user_data['concurso'] = query.data
    
    materias = DADOS_CONCURSOS[context.user_data['carreira']][query.data]
    # Organiza botões em duas colunas para não ficar gigante
    keyboard = [
        [InlineKeyboardButton(materias[i], callback_data=materias[i]),
         InlineKeyboardButton(materias[i+1], callback_data=materias[i+1])]
        for i in range(0, len(materias)-1, 2)
    ]
    if len(materias) % 2 != 0:
        keyboard.append([InlineKeyboardButton(materias[-1], callback_data=materias[-1])])

    await query.edit_message_text(text="Qual matéria deseja praticar?", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return ESCOLHER_MATERIA

async def escolher_quantidade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Passo 4: Quantidade de questões."""
    query = update.callback_query
    await query.answer()
    context.user_data['materia'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("5 Questões", callback_data="5")],
        [InlineKeyboardButton("10 Questões", callback_data="10")],
        [InlineKeyboardButton("20 Questões", callback_data="20")]
    ]
    await query.edit_message_text(text="Quantas questões vamos resolver agora?", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return ESCOLHER_QUANTIDADE

async def escolher_tempo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Passo 5: Tempo (Cronômetro)."""
    query = update.callback_query
    await query.answer()
    context.user_data['quantidade'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("⏱ Com Tempo (2min/q)", callback_data="com_tempo")],
        [InlineKeyboardButton("🧘 Modo Livre", callback_data="sem_tempo")]
    ]
    await query.edit_message_text(text="Como você quer responder?", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    return ESCOLHER_TEMPO

async def finalizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finaliza a configuração."""
    query = update.callback_query
    await query.answer()
    
    modo = "Com Cronômetro" if query.data == "com_tempo" else "Modo Livre"
    
    resumo = (
        "🚀 **TUDO PRONTO!**\n\n"
        f"📍 **Concurso:** {context.user_data['concurso']}\n"
        f"📖 **Matéria:** {context.user_data['materia']}\n"
        f"🔢 **Questões:** {context.user_data['quantidade']}\n"
        f"🕒 **Modo:** {modo}\n\n"
        "Estamos preparando o simulado para você..."
    )
    
    await query.edit_message_text(text=resumo, parse_mode="Markdown")
    return ConversationHandler.END

# --- EXECUÇÃO DO BOT ---

def main():
    # LEMBRETE: Substitua pelo seu Token real gerado no @BotFather
    TOKEN = "8695921152:AAFOLbNz0yVCCnHb9ipPCI42DRIT_bcRsak"
    
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("treinar", iniciar_treino)],
        states={
            ESCOLHER_CARREIRA: [CallbackQueryHandler(escolher_concurso)],
            ESCOLHER_CONCURSO: [CallbackQueryHandler(escolher_materia)],
            ESCOLHER_MATERIA: [CallbackQueryHandler(escolher_quantidade)],
            ESCOLHER_QUANTIDADE: [CallbackQueryHandler(escolher_tempo)],
            ESCOLHER_TEMPO: [CallbackQueryHandler(finalizar)],
        },
        fallbacks=[CommandHandler("treinar", iniciar_treino)],
    )

    app.add_handler(conv_handler)
    
    print("O Parceiro de Concursos está online! Pressione Ctrl+C para parar.")
    app.run_polling()

if __name__ == '__main__':
    main()