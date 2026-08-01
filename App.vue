<template>

<div class="chat">


<h2>
🤖 AI知识库助手
</h2>


<div class="answer">


<div
v-for="(msg,index) in messages"
:key="index"
:class="msg.role"
>


<p>
<b>
{{msg.role==="user"?"用户":"AI助手"}}
</b>
</p>


<p>
{{msg.content}}
</p>


</div>


</div>


<div class="input">


<input
v-model="question"
placeholder="请输入问题"
/>


<button @click="send">
发送
</button>


</div>


</div>


</template>



<script setup>

import {
ref
} from "vue"


const question=ref("")

const messages = ref([])



async function send(){

    if(!question.value.trim())
        return


    let q = question.value


    messages.value.push({
        role:"user",
        content:q
    })


    question.value=""


    // AI占位
    messages.value.push({
        role:"assistant",
        content:""
    })


    let aiIndex = messages.value.length - 1



    const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                query:q
            })
        }
    )


    const reader=response.body.getReader()

    const decoder=new TextDecoder()



    while(true){

        const {
            done,
            value
        } = await reader.read()


        if(done)
            break


        let text = decoder.decode(value,{
    stream:true
})


        text=text
        .replace(/data:/g,"")
        .replace(/\n\n/g,"")


        messages.value[aiIndex].content += text

    }

}


</script>



<style scoped>


.chat{

width:700px;

margin:50px auto;

}


.answer{

height:500px;

overflow-y:auto;

padding:20px;

background:#f5f5f5;

}



.user,
.assistant{

max-width:75%;

padding:12px 16px;

border-radius:12px;

margin:15px;

}



.user{

margin-left:auto;

background:#dbeafe;

}



.assistant{

margin-right:auto;

background:white;

border:1px solid #ddd;

}


.input{

display:flex;

gap:10px;

}


input{

flex:1;

height:35px;

font-size:16px;

}


button{

width:80px;

}


</style>
