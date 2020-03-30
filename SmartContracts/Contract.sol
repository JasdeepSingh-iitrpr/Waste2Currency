pragma solidity ^0.4.2;

contract W2C {
    
   int ecost=1;
   int fcost=1;
   
   struct Waste {
    string uuid;
    int wtype;
    int weight;
    address createdBy;
    address ownedBy;
    bool initialized;    
   }
   
   struct Entity{
       
       string name;
       string mno;
       address addr;
       bool initialized;
             
   }
   
   
   mapping(string  => Waste) private wasteStore;
   mapping(address =>Entity) private entityRecord;
   
   mapping(address => mapping(string => bool)) private walletStore;
   
   mapping(address => int) private Ecoins;
   mapping(address => int) private Fcoins;
   
   
   mapping(address => mapping(string=>bool)) private sent;
   mapping(address => mapping(string=>bool)) private received;
   
   
   event Bool(int);
   event EntityDetails(string name,string mno,address addr,int chk);
   event WasteDetails(string uuid,int wtype,int weight,address createdBy,address ownedBy,int chk);
   event Balance(int ,int,int);
   
   function CreateEntity(string name,string mno,address addr){
       
       if(entityRecord[msg.sender].initialized){
           emit Bool(0);
           return;
       }
       
       Ecoins[msg.sender]=1000;
       Fcoins[msg.sender]=1000;
       entityRecord[msg.sender] = Entity(name,mno,msg.sender,true);
       
       emit Bool(1);
       
   }

   
   function GetDetails(address addr){
       
        if(!entityRecord[msg.sender].initialized){
           
           emit EntityDetails("","",msg.sender,0);
           return;
       }
       
        emit EntityDetails(entityRecord[msg.sender].name,entityRecord[msg.sender].mno,entityRecord[msg.sender].addr,1);
       
       
   }
   
   function CreateWaste(string uuid,int wtype,int weight,address addr){
       
       if(wasteStore[uuid].initialized){
           
           emit Bool(0);
           return;
           
       }
       
       wasteStore[uuid] = Waste(uuid,wtype,weight,msg.sender,msg.sender,true);
       walletStore[msg.sender][uuid] = true;
       emit Bool(1);
       
   }
   
   function GetWasteDetails(string uuid,address addr){
       
         if(!wasteStore[uuid].initialized){
           
           emit WasteDetails("",0,0,msg.sender,msg.sender,0);
           return;
       }
       
        emit WasteDetails(uuid,wasteStore[uuid].wtype,wasteStore[uuid].weight,wasteStore[uuid].createdBy,wasteStore[uuid].ownedBy,1);
       
       
       
   }


   function SendRequest(address to,string uuid,address addr){
       
       if(!walletStore[msg.sender][uuid]){
           
           emit Bool(0);
           return;
       }
       
       sent[msg.sender][uuid] = true;
       received[to][uuid] = true;
       emit Bool(1);
       
       
   }
   
   function AcceptRequest(string uuid,address addr){
       
       
       if(!received[msg.sender][uuid]){
           emit Bool(-1);
           return;
       }
       
       
       address sender = wasteStore[uuid].ownedBy;
       sent[wasteStore[uuid].ownedBy][uuid] = false;
       received[msg.sender][uuid] = false;
       
       int cost;
       
       if(wasteStore[uuid].wtype==0){
           cost = wasteStore[uuid].weight*ecost;
           
           if(cost>=Ecoins[msg.sender]){
               
               Ecoins[msg.sender] = Ecoins[msg.sender]-cost;
               Ecoins[sender] = Ecoins[sender]+cost; 
               
           }
           else{
               
               emit Bool(0);
               return;
               
           }
           
          
       }
       
         if(wasteStore[uuid].wtype==1){
           cost = wasteStore[uuid].weight*fcost;
           
           if(cost>=Fcoins[msg.sender]){
               
                 Fcoins[msg.sender] = Fcoins[msg.sender]-cost;
                 Fcoins[sender] = Fcoins[sender]+cost;
               
           }
           else{
               
               emit Bool(0);
               return;
               
           }
           
          
       }
       
       wasteStore[uuid].ownedBy = msg.sender;
       
       walletStore[sender][uuid] = false;
       walletStore[msg.sender][uuid] = true;
     
       emit Bool(1);       
   }

   
   function getBalance(address addr){
       
       if(!entityRecord[msg.sender].initialized){
           return Balance(0,0,0);
       } 
       
       return Balance(Ecoins[msg.sender],Fcoins[msg.sender],1);
       
      
       
   }



}