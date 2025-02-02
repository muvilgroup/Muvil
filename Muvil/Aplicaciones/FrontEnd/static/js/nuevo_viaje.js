const btnNext = document.getElementById("btn-next");
const btnPrev = document.getElementById("btn-prev");
const btnPublish = document.getElementById("btn-publish");
const btnReturnYes = document.querySelector('#vuelta-radio label[for="vuelta-radio_0"]');
const btnReturnNo = document.querySelector('#vuelta-radio label[for="vuelta-radio_1"]');
let currentStepIndex = 0;
let currentStep;

if (btnNext && btnPrev) {
  btnNext.addEventListener("click", function() {
    if (!validateFields()) return;
    currentStep = document.querySelector(`.step-${currentStepIndex}`);
    currentStep.classList.add("d-none");
    currentStepIndex++;
    currentStep = document.querySelector(`.step-${currentStepIndex}`);
    currentStep.classList.remove("d-none");
    if (currentStepIndex == 5) {
      btnNext.classList.add("d-none");
    } else if (currentStepIndex == 10) {
      btnNext.classList.add("d-none");
      btnPublish.classList.remove("d-none");
    } else {
      btnPrev.classList.remove("invisible");
    }
  });
  btnPrev.addEventListener("click", function() {
    if (currentStepIndex == 0) return;
    currentStep = document.querySelector(`.step-${currentStepIndex}`);
    currentStep.classList.add("d-none");
    if (currentStepIndex == 10) {
      let selectedRadio = document.querySelector('input[name="flg_ida_vuelta"]:checked');
      if (selectedRadio.value == 'False') {
        currentStepIndex = 5;
      } else {
        currentStepIndex--;
      }
    } else {
      currentStepIndex--;
    }
    currentStep = document.querySelector(`.step-${currentStepIndex}`);
    currentStep.classList.remove("d-none");
    btnPublish.classList.add("d-none");
    if (currentStepIndex == 0) {
      btnPrev.classList.add("invisible");
    } else if (currentStepIndex == 5) {
      btnNext.classList.add("d-none");
    } else {
      btnNext.classList.remove("d-none");
    }
  });
}

if (btnReturnYes) {
  btnReturnYes.addEventListener("click", function() {
    currentStep = document.querySelector(`.step-${currentStepIndex}`);
    currentStep.classList.add("d-none");
    currentStepIndex = 6;
    currentStep = document.querySelector(`.step-${currentStepIndex}`);
    currentStep.classList.remove("d-none");
    btnNext.classList.remove("d-none");
    btnPrev.classList.remove("invisible");
  });
}

if (btnReturnNo) {
  btnReturnNo.setAttribute('data-bs-toggle', 'modal');
  btnReturnNo.setAttribute('data-bs-target', '#publicarviajeModal');
}

function validateFields() {
  const inputs = document.querySelectorAll(`.step-${currentStepIndex} input, .step-${currentStepIndex} select`);
  for (let input of inputs) {
    if (input.value.trim() === "") {
      input.classList.add("is-invalid");
      return false;
    }
    input.classList.remove("is-invalid");
  }
  return true;
}

const inputReturnMapping = [
  { 
    input: { id: "ciudad_origen", addressListSelector: "#ciudad_origen + .address-search-list" },
    return: { id: "campo_vuelta2", addressListSelector: "#campo_vuelta2 + .address-search-list" },
  },
  { 
    input: { id: "ciudad_destino", addressListSelector: "#ciudad_destino + .address-search-list" },
    return: { id: "campo_vuelta1", addressListSelector: "#campo_vuelta1 + .address-search-list" },
  },
];

inputReturnMapping.forEach(mapping => setupInputHandlers(mapping.input, mapping.return));

function setupInputHandlers(inputConfig, returnConfig = null) {
  const inputElement = document.getElementById(inputConfig.id);
  const addressList = document.querySelector(inputConfig.addressListSelector);
  let isValidInput = false; 

  inputElement.addEventListener("focus", function () {
    if (inputElement.value.trim() !== "") return;
    addressList.classList.remove("d-none");
    addressList.innerHTML = "";
    if (localizaciones) {
      document.addEventListener("click", function handleClickOutside(event) {
        if (
          addressList &&
          !addressList.contains(event.target) &&
          !inputElement.contains(event.target)
        ) {
          addressList.classList.add("d-none");
          document.removeEventListener("click", handleClickOutside);
        }
      });

      localizaciones.slice(0, 5).forEach(loc => {
        let locEl = document.createElement("div");
        locEl.innerHTML = loc.direccion;
        locEl.setAttribute("municipio", loc.municipio);
        locEl.classList.add("address-search-list-item", "rounded", "p-3");
        addressList.appendChild(locEl);

        locEl.addEventListener("click", function (event) {
          const selectedLocation = event.target.innerHTML;
          inputElement.value = selectedLocation;
          isValidInput = true;
          addressList.classList.add("d-none");

          if (returnConfig) {
            const returnElement = document.getElementById(returnConfig.id);
            if (returnElement) {
              returnElement.value = selectedLocation;
            }
          }
        });
      });
    }
  });

  inputElement.addEventListener("input", function () {
    const query = inputElement.value.trim().toLowerCase();
    isValidInput = false;
    if (query === "") {
      addressList.classList.add("d-none");
      return;
    }

    const filteredLocations = [];
    let count = 0;

    for (const loc of localizaciones) {
      if (loc.municipio.toLowerCase().includes(query)) {
        filteredLocations.push(loc);
        count++;
        if (count >= 15) break;
      }
    }

    addressList.innerHTML = "";

    if (filteredLocations.length > 0) {
      addressList.classList.remove("d-none");
      filteredLocations.forEach(loc => {
        let locEl = document.createElement("div");
        locEl.innerHTML = loc.direccion;
        locEl.classList.add("address-search-list-item", "rounded", "p-3");
        addressList.appendChild(locEl);

        locEl.addEventListener("click", function () {
          const selectedLocation = locEl.innerHTML;
          inputElement.value = selectedLocation;
          isValidInput = true;
          addressList.classList.add("d-none");

          if (returnConfig) {
            const returnElement = document.getElementById(returnConfig.id);
            if (returnElement) {
              returnElement.value = selectedLocation;
            }
          }
        });
      });
    } else {
      addressList.classList.add("d-none");
    }
  });

  inputElement.addEventListener("blur", function () {
    if (!isValidInput) {
      const isInList = localizaciones.some(loc => loc.direccion.toLowerCase().includes(inputElement.value.trim().toLowerCase()));

      if (!isInList) {
        inputElement.value = "";
      }
    }
  });
}
