import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from google import genai
from google.genai import types

from .personas import PERSONAS

GEMINI_MODEL = 'gemini-3.6-flash'


def _ask_gemini(contents, system_instruction=None):
    if not settings.GEMINI_API_KEY:
        return None, JsonResponse(
            {'error': 'GEMINI_API_KEY is missing from the .env file.'},
            status=500,
        )

    config_kwargs = {
        'automatic_function_calling': types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    }
    if system_instruction:
        config_kwargs['system_instruction'] = system_instruction

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    return response.text, None


def test_gemini(request):
    try:
        text, error_response = _ask_gemini('Say hello in one short sentence.')
        if error_response:
            return error_response
        return JsonResponse({'message': text})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@csrf_exempt
@require_POST
def explain(request):
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Send JSON with topic and persona.'},
            status=400,
        )

    topic = str(data.get('topic', '')).strip()
    persona = str(data.get('persona', '')).strip().lower()

    if not topic:
        return JsonResponse({'error': 'Please provide a topic.'}, status=400)

    if persona not in PERSONAS:
        return JsonResponse(
            {
                'error': 'Unknown persona.',
                'allowed': list(PERSONAS.keys()),
            },
            status=400,
        )

    try:
        text, error_response = _ask_gemini(
            f'Explain this topic: {topic}',
            system_instruction=PERSONAS[persona],
        )
        if error_response:
            return error_response
        return JsonResponse(
            {
                'topic': topic,
                'persona': persona,
                'explanation': text,
            }
        )
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)
