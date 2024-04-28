from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
import json
import random

with open('data.json', encoding='utf8') as file:
    questions = json.load(file)

BOT_TOKEN = '7134752919:AAGCqQM82B3rswT_BgYjxb84hgs3HjkHqFA'
markup = [['да', 'нет']]
reply_markup_yes_no = ReplyKeyboardMarkup(markup, one_time_keyboard=True)


def settings(context, questions_keys):
    """задает изначальные значения для context"""
    context.user_data['correct'] = 0
    context.user_data['current_question_num'] = 0
    random.shuffle(questions_keys)
    context.user_data['questions'] = questions_keys


async def start(update, context):
    questions_keys = list(questions.keys())
    settings(context, questions_keys)
    cur_question = questions[questions_keys[context.user_data['current_question_num']]]
    await update.message.reply_text(
        f"Вопрос №{context.user_data['current_question_num'] + 1}\n{cur_question['question']}")


async def check_text(update, context):
    answer = update.message.text

    if 'questions' not in context.user_data:  # пользователь написал, не начав тест
        questions_keys = list(questions.keys())  # начинаем тест, будто по команде /start
        settings(context, questions_keys)
        cur_question_data = questions[questions_keys[context.user_data['current_question_num']]]
        await update.message.reply_text(f"Вопрос №{context.user_data['current_question_num'] + 1}\n"
                                        f"{cur_question_data['question']}")
        return
    else:
        if context.user_data['current_question_num'] == 10:  # все вопросы были показаны
            if answer.lower() == "да":  # делаем тест по новой
                questions_keys = list(questions.keys())
                settings(context, questions_keys)
                cur_question_data = questions[questions_keys[context.user_data['current_question_num']]]
                await update.message.reply_text('Начинаю тест заново')
                await update.message.reply_text(f"Вопрос №{context.user_data['current_question_num'] + 1}\n"
                                                f"{cur_question_data['question']}")
                return

            elif answer.lower() == "нет":  # завершаем, как в случае /stop
                context.user_data.clear()  # очищаем словарь с пользовательскими данными
                await update.message.reply_text('Всего хорошего)')
                return ConversationHandler.END

            else:  # пользователь не ответил ни да, ни нет, ничего не делаем
                await update.message.reply_text("Я вас не понимаю. Хотите пройти тест заново?",
                                                reply_markup=reply_markup_yes_no)
                return

        cur_question_data = questions[context.user_data['questions'][context.user_data['current_question_num']]]
        correct_answer = cur_question_data['response']

        if correct_answer.lower() == answer.lower():
            context.user_data['correct'] += 1
            text = 'Правильно\n\n'
        else:
            text = (f'Упс, вопрос №{context.user_data["current_question_num"] + 1} ответ: '
                    f'{correct_answer}\n\n')

        context.user_data['current_question_num'] += 1
        if context.user_data['current_question_num'] == 10:
            await update.message.reply_text(f"Вы правильно ответили на {context.user_data['correct']} из 10 вопросов. "
                                            f"Хотите пройти тест еще раз?", reply_markup=reply_markup_yes_no)
            return

        cur_question_data = questions[context.user_data['questions'][context.user_data['current_question_num']]]
        question = cur_question_data['question']
        text += f"Вопрос №{context.user_data['current_question_num'] + 1}\n{question}"
        await update.message.reply_text(f"{text}")


async def stop(update, context):
    if 'correct' in context.user_data:
        await update.message.reply_text(f"Вы правильно ответили на {context.user_data['correct']} из 10 вопросов.\n"
                                        f"Всего хорошего) ")
    context.user_data.clear()  # очищаем словарь с пользовательскими данными
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler(["start"], start))
    application.add_handler(CommandHandler(["stop"], stop))
    text_handler = MessageHandler(filters.TEXT, check_text)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
