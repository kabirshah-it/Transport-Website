const steps = document.querySelectorAll(".form-step");

const nextButtons = document.querySelectorAll(".next-btn");

const backButtons = document.querySelectorAll(".back-btn");

const progressSteps = document.querySelectorAll(".progress-step");


let currentStep = 0;



function showStep(index){

    steps.forEach(step => {
        step.classList.remove("active");
    });


    progressSteps.forEach(step => {
        step.classList.remove("active");
    });


    steps[index].classList.add("active");

    progressSteps[index].classList.add("active");

}



function validateStep(){

    let inputs = steps[currentStep]
    .querySelectorAll(
        "input, select, textarea"
    );


    let valid = true;


    inputs.forEach(input => {


        if(input.hasAttribute("required")
            && input.value.trim() === ""){


            input.classList.add("input-error");

            valid = false;


        }else{

            input.classList.remove("input-error");

        }


    });


    return valid;

}



nextButtons.forEach(button => {


    button.addEventListener("click",()=>{


        if(validateStep()){


            if(currentStep < steps.length - 1){

                currentStep++;

                showStep(currentStep);

            }


        }


    });


});





backButtons.forEach(button=>{


    button.addEventListener("click",()=>{


        if(currentStep > 0){

            currentStep--;

            showStep(currentStep);

        }


    });


});