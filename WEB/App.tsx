import React, { useState, useEffect } from 'react';
import { Text, View, StyleSheet, TextInput, TouchableOpacity, FlatList } from 'react-native';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]); 
  const [inputText, setInputText] = useState('');
  const [isFinish, setIsFinish] = useState(false);

  useEffect(() => {
    const initialMessage: Message = {
      text: "Olá! 👋 Meu nome é CliniBot. Para que eu possa te ajudar, poderia me dizer seu nome e telefone?",
      sender: 'bot',
    };
    setMessages([initialMessage]);
  }, []);

  const sendMessage = async () => {
    if (inputText.trim() !== '') {
      const userMessage: Message = { text: inputText, sender: 'user' };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
  
      try {
        const response = await fetch('http://localhost:8080/1', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            texto: inputText,
          }), 
        });
  
        if (!response.ok) {
          throw new Error('Erro ao chamar a API');
        }
  
        const data = await response.json();
  
        if(data.resposta.includes("(validacao = true)")){
          data.resposta = data.resposta.replace("(validacao = true)", "");
          setIsFinish(true);
        }

        const botMessage: Message = {
          text: data.resposta || 'Resposta não encontrada', 
          sender: 'bot',
        };
  
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      } catch (error) {
        console.error('Erro:', error);
        const errorMessage: Message = {
          text: 'Ocorreu um erro ao enviar a mensagem',
          sender: 'bot',
        };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
      }
      finally {
        setInputText('');
      }
    }
  };

  const handleFinish = async () => {
    const response = await fetch('http://localhost:8080/finalizar/1', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    console.log(await response.json());
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View
      style={[
        styles.messageBubble,
        item.sender === 'user' ? styles.userBubble : styles.botBubble,
      ]}
    >
      <Text style={styles.messageText}>{item.text}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={messages}
        keyExtractor={(item, index) => index.toString()}
        renderItem={renderMessage}
        style={styles.chatHistory}
      />

      <View style={styles.inputContainer}>
        <TextInput
          style={[styles.input, isFinish && styles.disabledInput]}
          placeholder="Digite sua mensagem..."
          value={inputText}
          onChangeText={setInputText}
          editable={!isFinish} 
        />
        <TouchableOpacity 
          style={[styles.sendButton, isFinish && styles.disabledButton]} 
          onPress={sendMessage}
          disabled={isFinish} 
        >
          <Text style={[styles.sendButtonText, isFinish && styles.disabledButtonText]}>Enviar</Text>
        </TouchableOpacity>
      </View>

      {isFinish && (
        <TouchableOpacity style={styles.finishButton} onPress={handleFinish}>
          <Text style={styles.finishButtonText}>Finalizar</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#E6F7FF',
    justifyContent: 'flex-end',
  },
  chatHistory: {
    flex: 1,
    padding: 10,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    borderTopWidth: 1,
    borderColor: '#B3E5FC',
  },
  input: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 25,
    paddingHorizontal: 15,
    height: 40,
    borderColor: '#B3E5FC',
    borderWidth: 1,
  },
  disabledInput: {
    backgroundColor: '#d3d3d3', 
  },
  sendButton: {
    backgroundColor: '#4FC3F7',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 25,
    marginLeft: 10,
  },
  disabledButton: {
    backgroundColor: '#cccccc', 
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  disabledButtonText: {
    color: '#666666', 
  },
  messageBubble: {
    padding: 10,
    borderRadius: 20,
    marginBottom: 10,
    maxWidth: '80%',
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#4FC3F7',
  },
  botBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderColor: '#4FC3F7',
    borderWidth: 1,
  },
  messageText: {
    color: '#333',
  },
  finishButton: {
    position: 'absolute',
    top: '50%',
    alignSelf: 'center',
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  finishButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 18,
  },
});
