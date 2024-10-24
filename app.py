import os

from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

from utils.voiceflow_helpers import VoiceFlow

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        language = 'en-US'
        voice = 'alice'
        timeout = 5

        request_data = request.form

        tw_resp = VoiceResponse()

        vf = VoiceFlow(
            vf_id="670a7095de1278571e4736ac",
            vf_api_key="VF.DM.671948a921ddde63559a41ba.7JEErUu9i15u24A9",
            user_id=request_data['From'],
        )

        vf_messages = []

        if request_data['CallStatus'] == 'ringing':
            vf_messages = vf.interact(content_type='launch')

        else:
            if 'Digits' in request_data:
                digits = request_data['Digits']

                try:
                    choices = vf.fetch_state()['variables']['choices']
                except Exception as e:
                    print(e)
                else:
                    if choices != 0:
                        choices = choices.split('|')
                        if len(choices) >= int(digits):
                            vf_messages = vf.interact(
                                user_input=choices[int(digits) - 1]
                            )
                            vf.update_variable(
                                variable_name='choices',
                                variable_value=0,
                            )

                    else:
                        vf_messages = vf.interact(user_input=digits)

            elif 'SpeechResult' in request_data:
                vf_messages = vf.interact(
                    user_input=request_data['SpeechResult']
                )

        for message in vf_messages:
            if message.type == 'text':
                tw_resp.say(
                    message=message.data,
                    voice=voice,
                    language=language,
                )

            elif message.type == 'audio':
                tw_resp.play(
                    url=message.data,
                )

            elif message.type == 'choices':
                vf.update_variable(
                    variable_name='choices',
                    variable_value='|'.join(choice['name'] for choice in message.data),
                )

            elif message.type == 'call_forwarding':
                tw_resp.dial(message.data)

            elif message.type == 'end':
                tw_resp.hangup()

        tw_resp.gather(
            input='dtmf speech',
            language=language,
            timeout=timeout,
            speech_model='numbers_and_commands',
            finish_on_key='#',
            enhanced=True,
        )

        return str(tw_resp)

    else:
        return 'VoiceFlow - Twilio IVR'


if __name__ == '__main__':
    app.run()
