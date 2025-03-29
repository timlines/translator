
    // Replace these with your Azure Speech subscription key and region.
    const subscriptionKey = "YOUR_SUBSCRIPTION_KEY"; //"YOUR_SUBSCRIPTION_KEY"
    const serviceRegion = "southcentralus"; // e.g., "eastus" "YOUR_SERVICE_REGION"

    // Create the Speech Translation configuration.
    const speechTranslationConfig = SpeechSDK.SpeechTranslationConfig.fromSubscription(subscriptionKey, serviceRegion);
    speechTranslationConfig.speechRecognitionLanguage = "en-US";
    speechTranslationConfig.addTargetLanguage("es");

    // Create an audio configuration from the default microphone.
    const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();

    // Create the TranslationRecognizer instance.
    const recognizer = new SpeechSDK.TranslationRecognizer(speechTranslationConfig, audioConfig);

    const outputDiv = document.getElementById("output");

    // Update partial translation (in yellow).
    function updatePartial(text) {
      let partialElem = document.getElementById("partial");
      if (!partialElem) {
        partialElem = document.createElement("div");
        partialElem.id = "partial";
        partialElem.className = "partial";
        outputDiv.appendChild(partialElem);
      }
      partialElem.innerText = text;
      trimOutput();
    }

    // Append final translation (in white) and remove partial text.
    function addFinal(text) {
      // Remove partial text if present.
      const partialElem = document.getElementById("partial");
      if (partialElem) partialElem.remove();

      const finalElem = document.createElement("div");
      finalElem.className = "final";
      finalElem.innerText = text;
      outputDiv.appendChild(finalElem);

      trimOutput();
    }

    // Trim older content if total content height exceeds the visible area.
    function trimOutput() {
      // While the total content height is more than the container's height,
      // remove the oldest child (except keep the current partial if it exists).
      while (outputDiv.scrollHeight > outputDiv.clientHeight && outputDiv.firstChild) {
        outputDiv.removeChild(outputDiv.firstChild);
      }
    }

    // Subscribe to partial recognition updates.
    recognizer.recognizing = (s, e) => {
      const partialTranslation = e.result.translations.get("es");
      console.log("Partial translation:", partialTranslation);
      updatePartial(partialTranslation);
    };

    // Subscribe to final recognition events.
    recognizer.recognized = (s, e) => {
      if (e.result.reason === SpeechSDK.ResultReason.TranslatedSpeech) {
        const finalTranslation = e.result.translations.get("es");
        console.log("Final translation:", finalTranslation);
        addFinal(finalTranslation);
      } else if (e.result.reason === SpeechSDK.ResultReason.NoMatch) {
        console.log("No speech could be recognized.");
      }
    };

    recognizer.canceled = (s, e) => {
      console.error("Recognition canceled:", e);
    };

    recognizer.sessionStopped = (s, e) => {
      console.log("Session stopped.");
    };

    // On clicking "Start", trigger recognition and remove the start button.
    document.getElementById("startBtn").addEventListener("click", () => {
      recognizer.startContinuousRecognitionAsync(
        () => {
          console.log("Recognition started");
          outputDiv.innerHTML = ""; // Clear the output area.
          document.getElementById("startBtn").remove(); // Remove the button.
        },
        err => { console.error("Failed to start recognition:", err); }
      );
    });