import ollama
import pyttsx3
import streamlit as st
from PIL import Image
import ollama
import io
import base64
import time

### Helper functions

### Setting up Ollama client:
client = ollama.Client(
    host='http://localhost:11434',
    headers={'x-some-header': 'some-value'}
)

def extract_model_names(models_info):
    """
    Extracts the model names from the models information
    :param models_info: A dictionary containing the model's information.
    :return: A tuple containing the model names
    """
    return tuple(model["model"] for model in models_info["models"])

def image_to_bytes(image: Image.Image) -> bytes:
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    return img_bytes.getvalue()

def image_to_base64(image: Image.Image) -> str:
    """Converts a PIL Image to a base64-encoded string."""
    img_bytes = image_to_bytes(image)
    return base64.b64encode(img_bytes).decode('utf-8')

def describe_image(model: str, prompt: str, image: bytes, stream: bool = False) -> str:
    response = client.generate(
        model=model,
        prompt=prompt,
        images=[image]
    )
    return response

def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.1)

### App
st.title("🖼️ Image Descriptor app")

col1, col2 = st.columns(2)

with col1:
    input_method = st.segmented_control(
        label="Select input method",
        options=["Upload Image", "Take live picture"],
        selection_mode="single",
        default="Upload Image"
    )

    if input_method=="Upload Image":
        with st.container(border=True):
            st.write("Aquí va la descripción")
            picture = st.file_uploader(
                label="Upload your image to analyze",
                type=["jpg", "jpeg", "png"]
            )
            if picture:
                st.image(picture)

    elif input_method=="Take live picture":
        with st.container(border=True):
            enable = st.checkbox("Enable camera")
            picture = st.camera_input("Take a picture", disabled=not enable)


def text_to_audio(text: str, filename: str="description.mp3") -> str:
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

with col2:
    models_info = client.list()
    available_models = extract_model_names(models_info)

    if available_models:
        selected_model = st.selectbox(
            label="Pick a model available locally on your system",
            options=available_models,
        )
        if picture:
            pict = Image.open(picture)
            #pict_bytes = image_to_base64(pict)
            pict_bytes = image_to_bytes(pict)


            st.text("This is where you will type the prompt")
            prompt = st.text_area(
                label="Insert your prompt here",
                value="Describe what you see in the image."
            )
            if st.button(label="Generate description"):
                response = describe_image(
                    model=selected_model,
                    prompt=prompt,
                    image=pict_bytes,
                    stream=True
                )

                description_text = response["response"]

                audio_file = text_to_audio(description_text)
                with open(audio_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")

                st.write_stream(stream_text(description_text))

    else:
        st.warning("You have not selected any model from Ollama")




