import torch

def check_cuda_availability():
    print("PyTorch version:", torch.__version__)
    
    if torch.cuda.is_available():
        print("CUDA is available. GPU can be used.")
        print("Number of CUDA devices:", torch.cuda.device_count())
        
        for i in range(torch.cuda.device_count()):
            print(f"Device {i}: {torch.cuda.get_device_name(i)}")
        
        print("Current CUDA device:", torch.cuda.current_device())
        
        # Additional CUDA information
        print("CUDA capability:", torch.cuda.get_device_capability(torch.cuda.current_device()))
    else:
        print("CUDA is not available. Using CPU only.")

if __name__ == "__main__":
    check_cuda_availability()