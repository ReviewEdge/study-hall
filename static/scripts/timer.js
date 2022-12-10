let active = null; //set it to null at first in order to prevent toggle being used before loadTimer is finished
let timer, timer_div; //reference to the timer element and its parent object
let toggleBtn;
let timeLeft; //time left on the timer
let cycle; //number of work stints finished
let is_working; //whether this timer is a work timer or break timer
let num_loops_active = 0;

document.addEventListener("DOMContentLoaded", async () => {
    //get elements
    timer = document.getElementById("timer");
    timer_div = document.getElementById("timer-div");
    toggleBtn = document.getElementById("timer-toggle");
    const skipBtn = document.getElementById("timer-skip");
    //load the timer
    await fetch("/timer/status/")
        .then(validateJSON)
        .then(loadTimer);
    //set up the pause/play and skip buttons
    toggleBtn.addEventListener("click", toggle);
    skipBtn.addEventListener("click", changeState)
});

/**
 * sets the timer up with the data received from /timer/status/
 * @param {JSON} actionData the data for the current state of the timer
 */
async function loadTimer(actionData){
    /**
     * receive data from 
     * {
     * "a": active? (true=running, false=paused)
     * "w": working? (true=working, false=break)
     * "s": start time (only sent if running)
     * "t": time left in seconds (if start time is included, then remove time passed since starting)
     * "c": cycle number
     * }
     */
    timeLeft = actionData.t;
    cycle = actionData.c;
    if(actionData.w) {
        timer_div.className = "work";
        is_working = true;
    }
    else {
        timer_div.className = "break";
        is_working = false;
    }
    active = actionData.a;
    toggleBtn.innerText = active ? "Pause" : "Start";
    toggleBtn.className = active ? "btn btn-warning btn-sm":"btn btn-success btn-sm";
    if (active) {
        //if the timer is already active, then some other page must have started it
        timeLeft -= Math.floor((new Date()-new Date(actionData.s))/1000); //figure out how much time is left
        if(timeLeft <= 0){
            //if it somehow already finished during page transition, finish it
            changeState();
        }
        else{
            //otherwise resume the timer
            num_loops_active++;
            timerLoop();
        }
    }else{
        timer.innerText = timerText(timeLeft);
    }
}
/**
 * switches the timer between paused or running
 */
async function toggle(){
    if(active === null) return;//just in case
    if(active){
        //the timer is currently running, stop it and send how much time is left to python to put in session
        active = false;
        toggleBtn.innerText = "Start";
        toggleBtn.className = "btn btn-success btn-sm";
        fetch("/timer/pause/", {
            "method":"POST",
            "headers": {"Content-Type": "application/json"},
            "body": JSON.stringify({
                "t" : timeLeft,
                "w" : is_working
            })
        });
    }
    else{
        //the timer is currently paused, start it up and notify the python to put it in session
        fetch("/timer/start/", {
            "method":"POST",
            "headers": {"Content-Type": "application/json"},
            "body": JSON.stringify({
                "s" : new Date(), //send in current time
                "t" : timeLeft //as well as time left
            })
        });
        active = true;
        toggleBtn.innerText = "Pause";
        toggleBtn.className = "btn btn-warning btn-sm";
        num_loops_active++;
        timerLoop();
    }
}
/**
 * run when the timer runs out to switch betwen work or break.
 * also tells the server to pause the timer and set up a new one
 */
async function changeState(){
    //stop the timer
    active = false;
    toggleBtn.innerText = "Start";
    toggleBtn.className = "btn btn-success btn-sm";
    timer.innerText = "00:00";
    //figure out which mode is next
    if(is_working){
        is_working = false;
        cycle++;
        if(cycle%4 === 0){
            //long break
            timeLeft = 900;//15 min in seconds
        }
        else{
            //short break
            timeLeft = 300;//5 min in seconds
        }
        timer_div.className = "break";
    }
    else{
        is_working = true;
        timeLeft = 1500;//25 min in seconds
        timer_div.className = "work";
    }
    timer.innerText = timerText(timeLeft);
    fetch("/timer/pause/", {
        "method":"POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify({
            "t" : timeLeft,
            "w" : is_working,
            "c" : cycle
        })
    });
}
/**
 * call this to start the countdown of the timer
 * this function can be stopped by setting {active} to false or the timer running out
 */
function timerLoop(){
    if(num_loops_active > 1){
        num_loops_active--;
        return;
    }
    if(active){
        timer.innerText = timerText(timeLeft);
        timeLeft--;
        if(timeLeft <= 0){
            setTimeout(changeState, 1000);
            return;
        }
		setTimeout(timerLoop, 1000);
	}else{
        num_loops_active--;
    }
}
/**
 * 
 * @param {Integer} seconds the time left on the timer in seconds
 * @returns a string that is in the form MM:SS
 */
function timerText(seconds){
    const mins = Math.floor(seconds/60);
    const secs = seconds%60;
    return `${mins}:${secs<10 ? "0"+secs : ""+secs}`
}

/**
 * Validate a response to ensure the HTTP status code indcates success.
 * 
 * @param {Response} response HTTP response to be checked
 * @returns {object} object encoded by JSON in the response
 */
 function validateJSON(response) {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }
}