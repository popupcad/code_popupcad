#include <boost/bind.hpp>
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>

#include <gazebo/common/common.hh>
#include <stdio.h>
#include <iostream>
#include "velocity_message.pb.h"

namespace gazebo
{

  class ModelVel : public ModelPlugin
  {
    transport::NodePtr node;
    transport::PublisherPtr velPublisher;
    physics::WorldPtr world;


  public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
    {
	  // Store the pointer to the model
      this->model = _parent;
      this->world = this->model->GetWorld();
      node = transport::NodePtr(new transport::Node());
      // Initialize the node with the world name
      node->Init(world->GetName());
      velPublisher = node->Advertise<model_velocity::msgs::ModelVel_V>("~/default_bot/velocity");


      // Listen to the update event. This event is broadcast every
      // simulation iteration.
      this->updateConnection = event::Events::ConnectWorldUpdateBegin(
          boost::bind(&ModelVel::OnUpdate, this, _1));
    }

    // Called by the world update start event
    public: void OnUpdate(const common::UpdateInfo & /*_info*/)
    {
      // Apply a small linear velocity to the model.
      //this->model->SetLinearVel(math::Vector3(.03, 0, 0));
	//std::cout << this->model->GetWorldLinearVel();
    model_velocity::msgs::ModelVel_V res_v;
    for (physics::Link_V::const_iterator iter = this->model->GetLinks().begin();
            iter != this->model->GetLinks().end(); ++iter){
      model_velocity::msgs::ModelVelResponse* res = res_v.add_linkage();
      std::string name = (&*(*iter))->GetName();
      std::cout << name << " ";
      *res->mutable_name() = name;
      msgs::Vector3d angv = msgs::Convert((&*(*iter))->GetWorldAngularVel());
      std::cout << (&*(*iter))->GetWorldAngularVel() << " ";
      *res->mutable_angularvel() = angv;
      msgs::Vector3d angl = msgs::Convert((&*(*iter))->GetWorldLinearVel());
      std::cout << (&*(*iter))->GetWorldLinearVel() << " ";
      *res->mutable_linearvel() = angl;
    }
    velPublisher->Publish(res_v);
    }

    // Pointer to the model
    private: physics::ModelPtr model;

    // Pointer to the update event connection
    private: event::ConnectionPtr updateConnection;
  };

  // Register this plugin with the simulator
  GZ_REGISTER_MODEL_PLUGIN(ModelVel);
 
}
