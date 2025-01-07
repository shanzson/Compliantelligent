# Compliantelligent

- Set .env variables

- Run:
```pip3 install flask openai==0.28 python-dotenv
pip3 install python-dotenv
python app.py```

- Debugging:
If you get errors then make sure you have set the OpenAI API keys properly or not

- If python packages give error of `error: externally-managed-environment` then just using python virtual environment
```
python3 -m venv myenv
source myenv/bin/activate
pip install flask
python app.py
```

- Methodology:
We check whether there are openzeppelin standard libraries being imported
If they are being imported then we check if any standard EIP libraries are being imported or not
If they are being imported, then we check whether the imported EIP contracts are just being inherited or they are being intereacted with
If the current smart contract is interacting with the EIP contract such as an ERC20 token, then it means that the smart contract is not conforming to the 
EIP and the EIP standard Openzeppelin contract is just being used for interaction purposes
But if the smart contract is actually inheriting this standard EIP contract or standard then it means that it is conforming to the standard.