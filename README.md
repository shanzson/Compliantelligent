# Compliantelligent

# Try out the Project [Here](https://app.aiapocalypto.com/compliant)

# Target Users
- If you are a non-tech guy, a business head then this product is for you
- If you are a regulator then this product is for you
- If you are an investor and want to better understand a project, then this product
- If you are a platform and want to ensure compliance/self-compliance between projects, then this product is for you
 

- Set .env variables
- Run:
```pip3 install flask openai==0.28 python-dotenv
pip3 install python-dotenv
python app.py```

or

```
pip install -r requirements.txt
brew install python-flask
```
- Debugging:
If you get errors then make sure you have set the OpenAI API keys properly or not

- If python packages give error of `error: externally-managed-environment` then just using python virtual environment
```
python3 -m venv myenv
source myenv/bin/activate
pip install flask
python app.py
```

- For Solidityscan, make sure the following dependencies are met:
`solidityscan 0.2.1 requires requests==2.30.0, but you have requests 2.32.3 which is incompatible.`
`solidityscan 0.2.1 requires urllib3==1.26.4, but you have urllib3 2.3.0 which is incompatible.`

- Methodology:
We check whether there are openzeppelin standard libraries being imported
If they are being imported then we check if any standard EIP libraries are being imported or not
If they are being imported, then we check whether the imported EIP contracts are just being inherited or they are being intereacted with
If the current smart contract is interacting with the EIP contract such as an ERC20 token, then it means that the smart contract is not conforming to the 
EIP and the EIP standard Openzeppelin contract is just being used for interaction purposes
But if the smart contract is actually inheriting this standard EIP contract or standard then it means that it is conforming to the standard.