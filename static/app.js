const searchForm = document.getElementById('search_form')

let errorDisplay = document.getElementById('error_display')

const allowed_chars = "abcdefghijklmnopqrstuvwxyz,- '"

searchForm.addEventListener('submit', function(event){
    // verify that need to have ingredients have correct characters, and stop the search and display an error message if not. this is the most essential field--errors in other fields will be ignored.
    let needToHave = document.getElementById('need_to_have').value

    for (char of needToHave.toLowerCase()){
        if (allowed_chars.indexOf(char) === -1){
            event.preventDefault()
            errorDisplay.innerHTML = 'invalid character in must-have ingredients. please try again!'
        }
    }
})
