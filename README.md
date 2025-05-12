# CGUSAT

Federated Learning Report

What is Federated Learning?





Federated Learning is a machine learning technique that trains models without moving raw data to a central place.



Instead of sending data to a server, devices like phones or computers train the model locally using their own data.



Only the model updates (not the data itself) are sent to a central server to improve the model.

Why is it Important?





Privacy: Your data stays on your device, keeping it safe.



Efficiency: It uses the power of many devices, speeding things up.



Decentralization: No single server controls everything, reducing risks if something fails.

How Does it Work?





Start: A central server creates a basic model.



Send: The model is shared with many devices.



Train Locally: Each device improves the model using its own data.



Share Updates: Devices send only the changes (not the data) back to the server.



Combine: The server mixes all updates to make the model better.



Repeat: This process keeps going until the model works well.

Key Parts





Devices (Clients): Phones, computers, or anything with data to share.



Central Server: Manages the process but doesn’t see the raw data.



Model Updates: Small changes to the model based on local training.

Challenges





Communication: Sending updates can be slow with bad networks or lots of devices.



Differences: Devices may have unequal data or power, making it tricky.



Security: Updates might accidentally reveal some information if not protected well.

Where is it Used?





Smartphones: Improves things like text prediction or voice recognition without sharing your typing or voice.



Healthcare: Trains models on patient data from different hospitals while keeping it private.



Finance: Analyzes bank transactions across institutions without exposing personal details.

Advantages Over Traditional Machine Learning





Better Privacy: Data never leaves your device.



Less Data Transfer: Only small updates are sent, saving bandwidth.



Live Updates: The model improves as new data comes in.

Disadvantages





Complexity: It’s harder to set up than regular machine learning.



Device Demands: Needs devices with enough power and battery to train.



Coordination: Managing lots of devices can get messy.

What’s Next for Federated Learning?





Better Speed: New ideas to make it faster and easier.



Stronger Security: Ways to ensure updates don’t leak any info.



More Uses: Expanding to things like self-driving cars or smart home devices.

Conclusion

Federated Learning is a smart way to build machine learning models while keeping data private and using the power of many devices. It’s already helping in areas like phones and healthcare, and with some improvements, it could do even more in the future!
